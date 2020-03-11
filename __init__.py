import os
import functools
from flask import Flask, render_template, redirect, url_for, request, session, flash, g, app
from flask_migrate import Migrate
from urllib.parse import urlencode, quote, unquote
from werkzeug.security import generate_password_hash, check_password_hash
from flask_user import roles_required, UserManager 
from datetime import timedelta 

def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', default='dev'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    from .models import db, User, Note, Role, UserRoles, Department

    user_manager = UserManager(app, db, User)
    db.init_app(app)
    migrate = Migrate(app, db)

    def require_login(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            if not g.user:
                return redirect(url_for('log_in'))
            return view(**kwargs)
        return wrapped_view

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.before_request
    def load_user():
        user_id = session.get('user_id')
        if user_id:
            g.user = User.query.get(user_id)
            def make_session_permanent():
                session.permanent = True
                app.permanent_session_lifetime = timedelta(minutes=5)
        else:
            g.user = None



    @app.route('/sign_up', methods=('GET', 'POST'))
    def sign_up():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            error = None

            if not username:
                error = 'Username is required.'
            elif not password:
                error = 'Password is required.'
            elif User.query.filter_by(username=username).first():
                error = 'Username is already taken.'

            if error is None:
                user = User(username=username, password=generate_password_hash(password))
                db.session.add(user)
                db.session.commit()
                flash("Successfully signed up! Please log in.", 'success')
                return redirect(url_for('log_in'))

            flash(error, 'error')

        return render_template('sign_up.html')

    @app.route('/log_in', methods=('GET', 'POST'))
    def log_in():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            error = None

            user = User.query.filter_by(username=username).first()

            if not user or not check_password_hash(user.password, password):
                error = 'Username or password are incorrect'

            if error is None:
                session.clear()
                session['user_id'] = user.id
                return redirect(url_for('note_index'))

            flash(error, category='error')
        return render_template('log_in.html')

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/log_out', methods=('GET', 'DELETE'))
    def log_out():
        session.clear()
        flash('Successfully logged out.', 'success')
        return redirect(url_for('log_in'))

    @app.route('/notes')
    @require_login
    def note_index():
        return render_template('note_index.html', notes=g.user.notes)

    @app.route('/notes/new', methods=('GET', 'POST'))
    @require_login
    def note_create():
        if request.method == 'POST':
            title = request.form['title']
            body = request.form['body']
            error = None

            if not title:
                error = 'Title is required.'

            if not error:
                note = Note(author=g.user, title=title, body=body)
                db.session.add(note)
                db.session.commit()
                flash(f"Successfully created note: '{title}'", 'success')
                return redirect(url_for('note_index'))

            flash(error, 'error')

        return render_template('note_create.html')

    @app.route('/notes/<note_id>/edit', methods=('GET', 'POST', 'PATCH'))
    @require_login
    def note_update(note_id):
        note = Note.query.filter_by(user_id=g.user.id, id=note_id).first_or_404()
        if request.method in ['POST', 'PATCH']:
            title = request.form['title']
            body = request.form['body']
            error = None

            if not title:
                error = 'Title is required.'

            if not error:
                note.title = title
                note.body = body
                db.session.add(note)
                db.session.commit()
                flash(f"Successfully updated note: '{title}'", 'success')
                return redirect(url_for('note_index'))

            flash(error, 'error')

        return render_template('note_update.html', note=note)

    @app.route('/notes/<note_id>/delete', methods=('GET', 'DELETE'))
    @require_login
    def note_delete(note_id):
        note = Note.query.filter_by(user_id=g.user.id, id=note_id).first_or_404()
        db.session.delete(note)
        db.session.commit()
        flash(f"Successfully deleted note: '{note.title}'", 'success')
        return redirect(url_for('note_index'))

    def admin_required(f):
        @functools.wraps(f)
        def wrap(*args, **kwargs):
            if g.user.roles: 
                for role in g.user.roles:
                    if 'Admin' in role.name:
                        return f(*args, **kwargs)
                    else:
                        flash(u"You need to be an admin to view this page.", 'error')
                        return redirect(url_for('index'))
            else:
                flash(u"You need to be an admin to view this page.", 'error')
                return redirect(url_for('index'))
        return wrap

    @app.route('/users')
    @require_login 
    @admin_required
    def users_dashboard(user_id='g.user.id'):
        user_id = session.get('user_id')
        users = User.query.all()
        return render_template('users_dashboard.html', Users=users)

    @app.route('/roles')
    @require_login 
    @admin_required
    def roles_dashboard(user_id='g.user.id'):
        roles = Role.query.all()
        return render_template('roles_dashboard.html', Roles=roles)

    @app.route('/roles/new', methods=('GET', 'POST'))
    @require_login
    @admin_required
    def role_create():
        if request.method == 'POST':
            name = request.form['name']
            error = None

            if not name:
                error = 'Name is required.'

            if not error:
                role = Role(name=name)
                db.session.add(role)
                db.session.commit()
                flash(f"Successfully created role: '{name}'", 'success')
                return redirect(url_for('roles_dashboard'))

            flash(error, 'error')

        return render_template('role_create.html')

    @app.route('/departments')
    @require_login 
    def departments_dashboard(user_id='g.user.id'):
        from_url = 'departments_dashboard'
        departments = Department.query.all()
        return render_template('departments_dashboard.html', Departments=departments)

    @app.route('/departments/new', methods=('GET', 'POST'))
    @require_login
    @admin_required
    def department_create():
        if request.method == 'POST':
            title = request.form['title']
            error = None

            if not title:
                error = 'Title is required.'

            if not error:
                department = Department(title=title)
                db.session.add(department)
                db.session.commit()
                flash(f"Successfully created department: '{title}'", 'success')
                return redirect(url_for('departments_dashboard'))

            flash(error, 'error')

        return render_template('department_create.html')

    @app.route('/departments/<department_id>/edit', methods=('GET', 'POST', 'PATCH'))
    @admin_required
    @require_login
    def department_update(department_id):
        department = Department.query.filter_by(id=department_id).first_or_404()
        if request.method in ['POST', 'PATCH']:
            title = request.form['title']
            error = None

            if not title:
                error = 'Title is required.'

            if not error:
                department.title = title
                db.session.add(department)
                db.session.commit()
                flash(f"Successfully updated department: '{title}'", 'success')
                return redirect(url_for('departments_dashboard'))

            flash(error, 'error')

        return render_template('department_update.html', department=department)

    def confirmation_required(desc_fn):
        def inner(f):
            @functools.wraps(f)
            def wrapper(*args, **kwargs):
                if request.args.get('confirm') != '1':
                    desc = desc_fn()
                    return redirect(url_for('confirm', 
                        desc=desc, action_url=quote(request.url)))
                return f(*args, **kwargs)
            return wrapper
        return inner
    
    @app.route('/confirm')
    def confirm():
        desc = request.args['desc']
        action_url = unquote(request.args['action_url'])
    
        return render_template('_confirm.html', desc=desc, action_url=action_url)
    
    def you_sure():
        return "Are you sure?"
    
    @app.route('/departments/<department_id>/delete', methods=('GET', 'DELETE'))
    @require_login
    @admin_required
    @confirmation_required(you_sure)
    def department_delete(department_id):
        department = Department.query.filter_by(id=department_id).first_or_404()
        db.session.delete(department)
        db.session.commit()
        flash(f"Successfully deleted department: '{department.title}'", 'success')
        return redirect(url_for('departments_dashboard'))
 
    @app.route('/roles/<role_id>/delete', methods=('GET', 'DELETE'))
    @require_login
    @admin_required
    @confirmation_required(you_sure)
    def role_delete(role_id):
        role = Role.query.filter_by(id=role_id).first_or_404()
        db.session.delete(role)
        db.session.commit()
        flash(f"Successfully deleted role: '{role.name}'", 'success')
        return redirect(url_for('roles_dashboard'))
 
    return app

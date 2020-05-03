import os
import functools
from flask import Flask, render_template, redirect, url_for, request, session, flash, g, app
from flask_migrate import Migrate
from urllib.parse import urlencode, quote, unquote
from werkzeug.security import generate_password_hash, check_password_hash
from flask_user import roles_required, UserManager
from datetime import timedelta
import datetime
from flask import has_request_context, request
from flask.logging import default_handler

app.logger.removeHandler(default_handler)

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})


class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
        else:
            record.url = None
            record.remote_addr = None

        return super().format(record)

formatter = RequestFormatter(
    '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
    '%(levelname)s in %(module)s: %(message)s'
)
default_handler.setFormatter(formatter)


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', default='dev'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    from .models import db, User, Note, Role, UserRoles, Department, UserDepartments

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
        else:
            g.user = None
    def make_session_permanent():
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=5)



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
                app.logger.info('%s logged in successfully', user.username)
                return redirect(url_for('note_index'))

            flash(error, category='error')
        return render_template('log_in.html')

    @app.route('/')
    def index():
        x = datetime.datetime.now()
        day = x.strftime("%A")
        daynum = x.strftime("%d")
        month = x.strftime("%B")
        year = x.strftime("%Y")
        date = "Today is %s, the %s of %s %s" % day, daynum, month, year
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
                        flash(u"Insufficient permission.", 'error')
                        return redirect(url_for('index'))
            else:
                flash(u"Log in to view this page.", 'error')
                return redirect(url_for('index'))
        return wrap

    @app.route('/users')
    @require_login
    @admin_required
    def users_dashboard(user_id='g.user.id'):
        user_id = session.get('user_id')
        users = User.query.all()
        return render_template('users_dashboard.html', Users=users)

    @app.route('/users/new', methods=('GET', 'POST'))
    @require_login
    @admin_required
    def user_create():
        if request.method == 'POST':
            username = request.form['username']
            error = None

            if not name:
                error = 'Title is required.'

            if not error:
                user = User(name=name)
                db.session.add(user)
                db.session.commit()
                flash(f"Successfully created user: '{name}'", 'success')
                return redirect(url_for('users_dashboard'))

            flash(error, 'error')

        return render_template('user_create.html')

    @app.route('/users/<user_id>/edit', methods=('GET', 'POST', 'PATCH'))
    @require_login
    @admin_required
    def user_update(user_id):
        user = User.query.filter_by(id=user_id).first_or_404()
        roles = Role.query.all()
        departments = Department.query.all()
        rest = compare(user.departments, departments)
        if request.method in ['POST', 'PATCH']:
            username = request.form['username']
            name = request.form['name']
            title = request.form['title']
            error = None

            if not username:
                error = 'Username is required.'

            if not error:
                user.username = username
                db.session.add(user)
                updated_user = User.query.filter_by(username=username).first_or_404()
                department = Department.query.filter_by(title=title).first_or_404
                role = Role.query.filter_by(name=name).first_or_404()
                if (name and title) == 'None':
                    return render_template('user_update.html', user=user, user_id=user.id, roles=roles, departments=departments)
                elif 'None' in name:
                    updated_user.departments.append(department)
                    db.session.add(updated_user)
                    db.session.commit()
                    flash(f"Successfully added role: '{role.name}' to the user: '{username}'", 'success')
                    return render_template('user_update.html', user_id=user.id)
                elif 'None' in title:
                    updated_user.roles.append(role)
                    db.session.add(updated_user)
                    db.session.commit()
                    flash(f"Successfully added role: '{role.name}' to the user: '{username}'", 'success')
                    return render_template('user_update.html', user_id=user.id)
                else:
                    updated_user.departments.append(department)
                    updated_user.roles.append(role)
                    db.session.add(updated_user)
                    db.session.commit()
#                    flash(f"{user_name}, {updated_user}, {updated_user.roles[0].name}")
                    flash(f"Successfully added role: '{role.name}' and department '{department.title}' to the user '{user.username}'", 'success')
                    return render_template('user_update.html', user_id=user.id)

            flash(error, 'error')

        return render_template('user_update.html', user=user, roles=roles, departments=departments)

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

    @app.route('/roles/<role_id>/edit', methods=('GET', 'POST', 'PATCH'))
    @require_login
    def role_update(role_id):
        role = Role.query.filter_by(id=role_id).first_or_404()
        users = User.query.all()
        if request.method in ['POST', 'PATCH']:
            name = request.form['name']
            user_name = request.form.get('user_name')
            error = None

            if not name:
                error = 'Name is required.'

            if not error:
                role.name = name
                db.session.add(role)
                flash(f"Successfully updated role: '{name}'", 'success')
                if user_name == "None":
                    db.session.commit()
                    return render_template('role_update.html', role=role, users=users)
                else:
                    updated_user = User.query.filter_by(username=user_name).first_or_404()
                    updated_user.roles.append(role)
                    db.session.add(updated_user)
                    db.session.commit()
                    flash(f"{user_name}, {updated_user}, {updated_user.roles[0].name}")
                    return render_template('role_update.html', role=role, users=users)

            flash(error, 'error')

        return render_template('role_update.html', role=role, users=users)

    @app.route('/roles/<role_id>/<user_id>/delete', methods=('GET', 'DELETE'))
    @require_login
    @admin_required
    def user_role_delete(role_id, user_id):
        role = Role.query.filter_by(id=role_id).first_or_404()
        user = User.query.filter_by(id=user_id).first_or_404()
        users = User.query.all()
        user.roles.remove(role)
        db.session.add(user)
        db.session.commit()
        flash(f"Successfully deleted role \"{role.name}\" from user \"{user.username}\"", 'success')
        return render_template('role_update.html', role=role, users=users)

    @app.route('/departments')
    @require_login
    def departments_dashboard(user_id='g.user.id'):
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
        users = User.query.all()
        if request.method in ['POST', 'PATCH']:
            title = request.form['title']
            user_name = request.form.get('user_name')
            error = None

            if not title:
                error = 'Title is required.'

            if not error:
                department.title = title
                db.session.add(department)
                flash(f"Successfully updated department: '{title}'", 'success')
                if user_name == "None":
                    db.session.commit()
                    return render_template('department_update.html', department=department, users=users)
                else:
                    updated_user = User.query.filter_by(username=user_name).first_or_404()
                    updated_user.departments.append(department)
                    db.session.add(updated_user)
                    db.session.commit()
                    flash(f"{user_name}, {updated_user}, {updated_user.departments[0].title}")
                    return render_template('department_update.html', department=department, users=users)

            flash(error, 'error')

        return render_template('department_update.html', department=department, users=users)

    @app.route('/departments/<department_id>/delete', methods=('GET', 'DELETE'))
    @require_login
    @admin_required
    def department_delete(department_id):
        department = Department.query.filter_by(id=department_id).first_or_404()
        db.session.delete(department)
        db.session.commit()
        flash(f"Successfully deleted department: '{department.title}'", 'success')
        return redirect(url_for('departments_dashboard'))

    @app.route('/departments/<department_id>/delete/confirm', methods=('GET', 'POST'))
    @require_login
    @admin_required
    def confirm_delete_department(department_id):
        department = Department.query.filter_by(id=department_id).first_or_404()
        return render_template('confirm_delete_department.html', department=department)

    @app.route('/departments/<department_id>/<user_id>/delete', methods=('GET', 'DELETE'))
    @require_login
    @admin_required
    def user_department_delete(department_id, user_id):
        department = Department.query.filter_by(id=department_id).first_or_404()
        user = User.query.filter_by(id=user_id).first_or_404()
        users = User.query.all()
        user.departments.remove(department)
        db.session.add(user)
        db.session.commit()
        flash(f"Successfully deleted department \"{department.title}\" from user \"{user.username}\"", 'success')
        return render_template('department_update.html', department=department, users=users)

    @app.route('/roles/<role_id>/delete/confirm', methods=('GET', 'POST'))
    @require_login
    @admin_required
    def confirm_delete_role(role_id):
        role = Role.query.filter_by(id=role_id).first_or_404()
        return render_template('confirm_delete_role.html', role=role)

    @app.route('/roles/<role_id>/delete', methods=('GET', 'DELETE'))
    @require_login
    @admin_required
    def role_delete(role_id):
        role = Role.query.filter_by(id=role_id).first_or_404()
        db.session.delete(role)
        db.session.commit()
        flash(f"Successfully deleted role: '{role.name}'", 'success')
        return redirect(url_for('roles_dashboard'))

    @app.route('/<variable>/<variable_id>/delete/confirm', methods=('GET', 'POST'))
    @require_login
    @admin_required
    def confirm_delete(variable_id, variable):
        departments = Department.query.all()
        roles = Role.query.all()

        for department in departments:
            if department.title in variable:
                variable = Department.query.filter_by(id=variable_id).first_or_404().title
                variables_dashboard = "departments_dashboard"
                return render_template('confirm_delete.html', variable=variable, variables_dashboard=variables_dashboard)

        for role in roles:
            if role.name in variable:
                variable = Role.query.filter_by(id=variable_id).first_or_404().name
                variables_dashboard = "roles_dashboard"
                return render_template('confirm_delete.html', variable=variable, variables_dashboard=variables_dashboard)


    def compare(list1, list2):
        set_difference = set(list1) - set(list2)
        list_difference = list(set_difference)
        return list_difference



    return app

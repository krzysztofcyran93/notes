pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        sh """
        sudo -s ls /home/centos/.local/share/virtualenvs/notes-scW2TLqU/bin/activate
        git status
        """
      }
    }
  }
}

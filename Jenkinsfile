pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        sh """
        hostname
        whoami
        pwd
        ls
        . /home/centos/.local/share/virtualenvs/notes-scW2TLqU/bin/activate
        cat findings.txt
        git fetch
        git status
        """
      }
    }
  }
}

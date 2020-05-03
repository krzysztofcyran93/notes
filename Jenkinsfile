pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        sh """
        pwd
        cd /home/centos/notes/
        git status
        """
      }
    }
  }
}

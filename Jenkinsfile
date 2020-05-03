pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        sh """
        pwd
        sudo cd /home/centos/notes/
        git status
        """
      }
    }
  }
}

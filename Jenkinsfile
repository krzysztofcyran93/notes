pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        sh """
        pwd
        sudo ls /home/centos/notes
        git status
        """
      }
    }
  }
}

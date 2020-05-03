pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        sh """
        pwd
        sudo -s ls /home/centos/
        git status
        """
      }
    }
  }
}

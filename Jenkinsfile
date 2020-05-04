pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        sh """
        whoami
        pwd
        sudo su - centos & ls -lrt > findings.txt
        """
        sh """
        cat findings.txt
        git fetch
        git status
        """
      }
    }
  }
}

pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        sh """
        whoami
        pwd
        sudo su - centos & pwd & cd ~/ & ls -lrt
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

pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        sh """
        whoami
        pwd
        sudo su - centos & ls -lrt > new_findings.txt
        """
        sh """
        pwd
        git fetch
        git status
        """
      }
    }
  }
}

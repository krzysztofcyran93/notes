pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        sh """
        whoami
        pwd
        sudo ls /home/centos/notes > findings.txt
        cat findings.txt
        git fetch
        git status
        """
      }
    }
  }
}

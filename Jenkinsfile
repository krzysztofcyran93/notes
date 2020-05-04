pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        sh """
        hostname
        whoami
        pwd
        ls /home/centos/notes > findings.txt
        cat findings.txt
        git fetch
        git status
        """
      }
    }
  }
}

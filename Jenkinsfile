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
        sudo find . -type f -iname "activate" > findings.txt
        cat findings.txt
        git fetch
        git status:w
        """
      }
    }
  }
}

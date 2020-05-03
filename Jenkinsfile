pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        sh """
        whoami
        pwd
        ls
        sudo find . -type f -iname "activate" > findings.txt
        git status
        git fetch
        """
      }
    }
  }
}

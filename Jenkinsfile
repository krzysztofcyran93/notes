pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        sh """
        who
        pwd
        ls
        sudo find . -type f -iname "activate"
        git status
        git fetch
        """
      }
    }
  }
}

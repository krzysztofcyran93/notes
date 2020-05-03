pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        sh """
        who
        pwd
        ls
        pipenv shell
        git status
        git fetch
        """
      }
    }
  }
}

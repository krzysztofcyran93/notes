pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        sh 'git status'
        sh 'git pull notes stage'
      }
    }
  }
}

pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        sh 'cd /home/centos/notes'
        sh 'pipenv shell'
        sh 'git status'
        sh 'git pull notes master'
      }
    }
  }
}

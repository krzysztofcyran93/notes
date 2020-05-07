pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        sh """
        whoami
        pwd
        sudo cat "$(ls -lrt /opt/)" >> /opt/cat.txt
        """
      }
    }
  }
}

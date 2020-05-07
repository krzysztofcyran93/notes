pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        sh """
        whoami
        pwd
        ls -lrt /opt/ >> /opt/cat.txt
        """
      }
    }
  }
}

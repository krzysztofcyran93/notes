pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        sh """
        whoami
        pwd
        cat 'ls -lrt /opt' > /opt/cat.txt
        """
      }
    }
  }
}

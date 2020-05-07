pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        sh """
        whoami
        pwd
        echo "ls -lrt /opt/" >> /opt/cat.txt
        """
      }
    }
  }
}

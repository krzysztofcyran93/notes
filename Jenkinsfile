pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        sh """
        pwd
        sudo -s source /home/jenkins/.local/share/virtualenvs/jenkins-39SWxFAg/bin/activate
        git status
        """
      }
    }
  }
}

pipeline {

    agent any

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                sh 'python -m pip install -r requirements.txt'
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t weather-app:%BUILD_NUMBER% .'
            }
        }
    }
}

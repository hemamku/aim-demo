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
                bat 'python -m pip install -r requirements.txt'
            }
        }

        stage('Docker Build') {
            steps {
                bat 'docker build -t weather-app:%BUILD_NUMBER% .'
            }
        }
    }
}

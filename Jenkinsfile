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
                echo 'Application source code checked out successfully.'
                echo 'Python dependencies will be installed inside the Docker image.'
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t weather-app:latest .'
            }
        }
    }
}

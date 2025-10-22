pipeline {
    agent any // Run on any available Jenkins agent

    // Environment variables used throughout the pipeline
    environment {
        DOCKER_HUB_CREDS = credentials('dockerhub-creds') // The ID you set in Jenkins
        KUBECONFIG_CREDS = credentials('kubeconfig-creds') // The ID you set in Jenkins
        DOCKER_HUB_USER = "yourdockerhubusername"
        APP_NAME = "my-web-app"
        DOCKER_IMAGE = "${DOCKER_HUB_USER}/${APP_NAME}:${env.BUILD_NUMBER}" // e.g., yourdockerhubusername/my-web-app:1
    }

    stages {
        stage('2. Build Docker Image') {
            steps {
                script {
                    // Builds the Docker image using the Dockerfile in your repo
                    echo "Building image: ${DOCKER_IMAGE}"
                    docker.build(DOCKER_IMAGE, '.')
                }
            }
        }

        stage('3. Push to Docker Hub') {
            steps {
                script {
                    // Logs into Docker Hub using the stored credentials and pushes the image
                    docker.withRegistry('https://registry.hub.docker.com', DOCKER_HUB_CREDS) {
                        echo "Pushing image: ${DOCKER_IMAGE}"
                        docker.image(DOCKER_IMAGE).push()
                    }
                }
            }
        }

        stage('4. Deploy to Kubernetes') {
            steps {
                // This block makes the kubeconfig file available for kubectl commands
                withKubeConfig([credentialsId: KUBECONFIG_CREDS]) {
                    // Replace the placeholder in the deployment file with the actual image name
                    sh "sed -i 's|IMAGE_PLACEHOLDER|${DOCKER_IMAGE}|g' deployment.yaml"

                    // Apply the updated deployment and the service manifest to your cluster
                    echo "Applying Kubernetes manifests..."
                    sh "kubectl apply -f deployment.yaml"
                    sh "kubectl apply -f service.yaml"

                    // Wait for the deployment to complete successfully
                    echo "Waiting for rollout to complete..."
                    sh "kubectl rollout status deployment/my-web-app"
                }
            }
        }
    }
}

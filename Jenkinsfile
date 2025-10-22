pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        timestamps()
    }

    parameters {
        string(name: 'DOCKER_REGISTRY', defaultValue: 'docker.io', description: 'Docker registry (eg. docker.io or 123456789012.dkr.ecr.us-east-1.amazonaws.com)')
        string(name: 'DOCKER_REPO', defaultValue: 'varunmaran/my-web-app', description: 'Repository/name for the image')
        string(name: 'K8S_NAMESPACE', defaultValue: 'default', description: 'Kubernetes namespace to deploy into')
    }

    environment {
        IMAGE_TAG = "${env.BUILD_NUMBER}"
        DOCKER_IMAGE = "${params.DOCKER_REGISTRY}/${params.DOCKER_REPO}:${IMAGE_TAG}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Check Prerequisites') {
            steps {
                script {
                    // Check if Docker is installed
                    def dockerCheck = sh(script: 'which docker', returnStatus: true)
                    if (dockerCheck != 0) {
                        error "Docker is not installed on this agent. Please install Docker first."
                    }
                    
                    // Check Docker daemon is running
                    def dockerInfo = sh(script: 'docker info', returnStatus: true)
                    if (dockerInfo != 0) {
                        error "Docker daemon is not running or current user doesn't have permission to access it."
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    try {
                        echo "Building image ${DOCKER_IMAGE}"
                        sh "docker build -t ${DOCKER_IMAGE} ."
                    } catch (Exception e) {
                        error "Failed to build Docker image: ${e.getMessage()}"
                    }
                }
            }
        }

        stage('Push Image') {
            steps {
                script {
                    // Uses the Jenkins credential id 'dockerhub-creds' (username/password) configured in Jenkins
                    docker.withRegistry("https://${params.DOCKER_REGISTRY}", 'dockerhub-creds') {
                        echo "Pushing image ${DOCKER_IMAGE}"
                        docker.image("${DOCKER_IMAGE}").push()
                        // Also push the 'latest' tag if desired
                        docker.image("${DOCKER_IMAGE}").push('latest')
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                script {
                    // Make kubeconfig available via credentials id 'kubeconfig-creds' (Secret File)
                    withKubeConfig([credentialsId: 'kubeconfig-creds']) {
                        echo "Updating deployment image to ${DOCKER_IMAGE} in namespace ${params.K8S_NAMESPACE}"

                        // Try to update the existing deployment image; if deployment does not exist, apply manifests
                        def setImageCmd = "kubectl set image deployment/my-web-app my-web-app-container=${DOCKER_IMAGE} -n ${params.K8S_NAMESPACE} --record"
                        def applyCmd = "kubectl apply -f deployment.yaml -n ${params.K8S_NAMESPACE} && kubectl apply -f service.yaml -n ${params.K8S_NAMESPACE}"

                        // Run set image; if it fails (deployment missing) fall back to apply
                        sh "${setImageCmd} || ${applyCmd}"

                        // Update APP_VERSION env on the deployment for visibility
                        sh "kubectl set env deployment/my-web-app APP_VERSION=${IMAGE_TAG} -n ${params.K8S_NAMESPACE} || true"

                        // Wait for rollout to complete
                        sh "kubectl rollout status deployment/my-web-app -n ${params.K8S_NAMESPACE}"
                    }
                }
            }
        }
    }

    post {
        success {
            echo "Deployment successful: ${DOCKER_IMAGE}"
        }
        failure {
            echo "Pipeline failed"
        }
    }
}
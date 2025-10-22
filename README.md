# CI/CD pipeline for Dockerized Flask app -> Kubernetes via Jenkins

This repository contains a minimal Flask app, Dockerfile, Kubernetes manifests, and a Jenkins pipeline (`Jenkinsfile`) that builds a Docker image, pushes it to a registry, and deploys it to a Kubernetes cluster.

## Files

- `app.py` - simple Flask app that reads `APP_VERSION` env var.
- `Dockerfile` - builds the app image.
- `deployment.yaml` - Kubernetes Deployment (contains IMAGE_PLACEHOLDER and IMAGE_TAG_PLACEHOLDER).
- `service.yaml` - Kubernetes Service exposing the app.
- `Jenkinsfile` - Declarative Jenkins pipeline to build, push, and deploy.

## Jenkins setup (minimal)

1. Install Jenkins and required plugins:
   - Docker Pipeline
   - Kubernetes CLI Plugin (kubectl integration)
   - Credentials Binding

2. Add credentials in Jenkins (Manage Jenkins -> Credentials):
   - ID: `dockerhub-creds` (Username with password) — credentials for the Docker registry.
   - ID: `kubeconfig-creds` (Secret file) — your `kubeconfig` file allowing Jenkins to access the cluster.

3. Create a Jenkins Pipeline job and point it to this repository. The `Jenkinsfile` uses parameters:
   - `DOCKER_REGISTRY` (default `docker.io`)
   - `DOCKER_REPO` (default `yourdockerhubusername/my-web-app`)
   - `K8S_NAMESPACE` (default `default`)

4. Configure agent nodes that can run Docker builds, or use a Docker-in-Docker capable agent. Ensure `docker` CLI is available for the Jenkins agent.

## How it works

- The pipeline builds an image tagged with the Jenkins `BUILD_NUMBER` and pushes it to the registry.
- The pipeline then deploys to Kubernetes using `kubectl` (kubeconfig from credentials). It will attempt to `kubectl set image` on an existing deployment and falls back to applying the manifests.
- `deployment.yaml` contains `IMAGE_PLACEHOLDER` and `IMAGE_TAG_PLACEHOLDER` so manual replacement or CI replacement is possible.

## Quick verification

1. Trigger a build in Jenkins.
2. After success, check the deployment in Kubernetes:
   - kubectl get deployments -n <namespace>
   - kubectl get pods -n <namespace>
   - kubectl get svc -n <namespace>

3. Access the app via NodePort or LoadBalancer depending on `service.yaml` type.

## Next steps / Recommendations

- Use a private registry or cloud-native registries (ECR/GCR/ACR) for production.
- Consider switching to Helm for templating manifests and managing releases.
- Add health checks and readiness/liveness probes to the deployment.
- Add CI tests and security scanning (image scanning, SCA).

---

If you want, I can also:
- Convert the manifests to Helm templates.
- Add a small GitHub Actions or local script to build images for local testing.

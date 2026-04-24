pipeline {
    agent any

    environment {
        IMAGE_NAME = "ocr-engine"
        IMAGE_TAG  = "v3"
        REGISTRY   = "vcr.vngcloud.vn/105622-ai-platform-nonprod"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }


        stage('Build') {
            steps {
                sh '''
                  IMAGE="$IMAGE_NAME:$IMAGE_TAG"
                  docker build -t "$IMAGE" .
                '''
            }
        }

        stage('Scan Image (Trivy)') {
            steps {
                sh '''
                  IMAGE="$IMAGE_NAME:$IMAGE_TAG"
                  docker run --rm \
                    -v /var/run/docker.sock:/var/run/docker.sock \
                    -v /data/trivy/trivy-db:/root/.cache/trivy \
                    aquasec/trivy:latest image \
                    --skip-db-update \
                    --severity HIGH,CRITICAL \
                    --exit-code 0 \
                    "$IMAGE"
                '''
            }
        }

        stage('Push') {
            steps {
                sh '''
                  IMAGE="$IMAGE_NAME:$IMAGE_TAG"
                  REGISTRY_IMAGE="$REGISTRY/$IMAGE_NAME:$IMAGE_TAG"

                  docker tag "$IMAGE" "$REGISTRY_IMAGE"
                  docker push "$REGISTRY_IMAGE"
                '''
            }
        }
    }

    post {
        always {
            sh 'docker logout vcr.vngcloud.vn || true'
        }
    }
}

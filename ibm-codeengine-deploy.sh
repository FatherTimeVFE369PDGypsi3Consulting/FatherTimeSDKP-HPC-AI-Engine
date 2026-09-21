#!/usr/bin/env bash
set -euo pipefail

APP_NAME="${APP_NAME:-fathertime-hpc}"
REGISTRY_NAMESPACE="${REGISTRY_NAMESPACE:-your-namespace}"
RESOURCE_GROUP="${RESOURCE_GROUP:-your-resource-group}"
IMAGE="us.icr.io/${REGISTRY_NAMESPACE}/${APP_NAME}:latest"

echo "Logging in to IBM Cloud..."
ibmcloud login --sso
ibmcloud target -g "${RESOURCE_GROUP}"

echo "Installing required plugins..."
ibmcloud plugin install code-engine || true
ibmcloud plugin install container-registry || true

echo "Creating Code Engine project if it does not exist..."
ibmcloud ce project create --name "${APP_NAME}" || true
ibmcloud ce project select --name "${APP_NAME}"

echo "Logging in to IBM Container Registry..."
ibmcloud cr login
ibmcloud cr namespace-add "${REGISTRY_NAMESPACE}" || true

echo "Building Docker image: ${IMAGE}"
docker build -t "${IMAGE}" .
docker push "${IMAGE}"

echo "Creating Code Engine app..."
ibmcloud ce app create "${APP_NAME}" \
  --image "${IMAGE}" \
  --port 8080 \
  --min-scale 1 \
  --max-scale 2 \
  --cpu 1 \
  --memory 2G \
  --env PORT=8080 \
  --env APP_URL="https://${APP_NAME}.us-south.codeengine.appdomain.cloud"

echo "Deployment script complete."
echo "Use: ibmcloud ce app get --name ${APP_NAME}"

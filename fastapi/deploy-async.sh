#!/bin/bash
# deploy-async.sh

set -e

export PROJECT_ID=$(gcloud config get-value project)
export REGION="asia-south1"
export INSTANCE_NAME="fastapi-db"

# Get database connection details
export DB_HOST=$(gcloud sql instances describe $INSTANCE_NAME --format='value(ipAddresses[0].ipAddress)')
export DB_PASSWORD="fastapiDB@12"

# Build and deploy
gcloud builds submit --config=cloudbuild.yaml \
    --substitutions=_DB_HOST=$DB_HOST,_DB_PASSWORD=$DB_PASSWORD

echo "Deployment completed!"

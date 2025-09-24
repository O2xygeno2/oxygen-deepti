#!/bin/bash
# deploy-async.sh

set -e

# project details
export PROJECT_ID=$(gcloud config get-value project)
export REGION="asia-south1"

# Get database connection details
export INSTANCE_NAME="fastapi-db"
export DB_HOST=$(gcloud sql instances describe $INSTANCE_NAME --format='value(ipAddresses[0].ipAddress)')
export DB_PASSWORD="fastapiDB@12"

echo "Deploying FastAPI app to Cloud Run..."

gcloud builds submit --tag gcr.io/$PROJECT_ID/oxygen-fastapi-app

gcloud run deploy oxygen-fastapi-app \
    --image gcr.io/$PROJECT_ID/oxygen-fastapi-app \
    --platform managed \
    --region $REGION \
    --vpc-connector oxygen-vpc-connector \
    --set-env-vars="DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,DB_HOST=10.231.0.3,DB_NAME=$DB_NAME" \
    --cpu=2 \
    --memory=2Gi \
    --allow-unauthenticated

echo "Deployment completed!"

#!/bin/bash
set -euo pipefail

PROJECT_ID="rebellis-production"
REGION="us-central1"

echo "Setting up GCP project..."

gcloud projects create $PROJECT_ID --name="Rebellis Production"

gcloud services enable \
  compute.googleapis.com \
  container.googleapis.com \
  sqladmin.googleapis.com \
  --project=$PROJECT_ID

echo "GCP project setup complete!"

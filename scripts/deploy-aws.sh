#!/usr/bin/env bash
set -euo pipefail

AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID:-}"
ECR_REPO="${ECR_REPO:-northstar-market}"
CLUSTER_NAME="${CLUSTER_NAME:-northstar-market-cluster}"
SERVICE_NAME="${SERVICE_NAME:-northstar-market-service}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

if [[ -z "$AWS_ACCOUNT_ID" ]]; then
  echo "AWS_ACCOUNT_ID is required. Example: export AWS_ACCOUNT_ID=123456789012" >&2
  exit 1
fi

aws ecr describe-repositories --repository-names "$ECR_REPO" --region "$AWS_REGION" >/dev/null 2>&1 || \
  aws ecr create-repository --repository-name "$ECR_REPO" --region "$AWS_REGION"

aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

docker build -t "$ECR_REPO:$IMAGE_TAG" .
docker tag "$ECR_REPO:$IMAGE_TAG" "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:$IMAGE_TAG"
docker push "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:$IMAGE_TAG"

aws ecs update-service \
  --cluster "$CLUSTER_NAME" \
  --service "$SERVICE_NAME" \
  --force-new-deployment \
  --region "$AWS_REGION" >/dev/null

echo "Deployment request sent for $SERVICE_NAME."
echo "If this is the first deployment, register the ECS task definition and create the service using the JSON in aws/ecs-task-definition.json."

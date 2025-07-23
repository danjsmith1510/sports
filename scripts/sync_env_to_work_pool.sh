#!/bin/bash

# Usage: ./scripts/sync_env_to_work_pool.sh <pool_name>

POOL_NAME="$1"

if [ -z "$POOL_NAME" ]; then
  echo "❌ Error: Pool name not provided"
  exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
  echo "❌ .env file not found!"
  exit 1
fi

# Convert .env to key=value arguments
ENV_ARGS=$(grep -v '^#' .env | grep '=' | xargs)

echo "🔄 Setting environment variables in work pool '$POOL_NAME'..."
prefect work-pool set-env "$POOL_NAME" $ENV_ARGS
#!/bin/bash

# Azure APIM Backend Pool Session Affinity Configuration Script (REST API Version)
# This script updates an existing APIM backend pool to enable session affinity using REST API

set -e

# Configuration variables - update these for your environment
RESOURCE_GROUP="<your-resource-group-name>"
APIM_SERVICE_NAME="<your-apim-instance-name>"
BACKEND_POOL_ID="<backend-pool-name>"
SUBSCRIPTION_ID=""

# Check if required tools are installed
if ! command -v az &> /dev/null; then
    echo "Error: Azure CLI is not installed. Please install it first."
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo "Error: jq is not installed. Please install it first (brew install jq)."
    exit 1
fi

# Check if logged into Azure
if ! az account show &> /dev/null; then
    echo "Error: Not logged into Azure. Please run 'az login' first."
    exit 1
fi

# Get subscription ID if not provided
if [ -z "$SUBSCRIPTION_ID" ]; then
    echo "Getting current subscription ID..."
    SUBSCRIPTION_ID=$(az account show --query "id" --output tsv)
    echo "Using subscription: $SUBSCRIPTION_ID"
fi

echo "Updating APIM backend pool to enable session affinity..."

# Construct the REST API URL
API_URL="/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.ApiManagement/service/$APIM_SERVICE_NAME/backends/$BACKEND_POOL_ID?api-version=2023-05-01-preview"

# Get current backend pool configuration using REST API
echo "Retrieving current backend pool configuration..."
echo "URL: $API_URL"
CURRENT_CONFIG=$(az rest \
    --method GET \
    --url "$API_URL")

if [ $? -ne 0 ]; then
    echo "Error: Failed to retrieve backend configuration. Please check your resource names."
    exit 1
fi

echo "Current configuration retrieved successfully."

# Check if it's a pool type backend
BACKEND_TYPE=$(echo "$CURRENT_CONFIG" | jq -r '.properties.type')
if [ "$BACKEND_TYPE" != "Pool" ]; then
    echo "Error: Backend '$BACKEND_POOL_ID' is not a Pool type backend (found: $BACKEND_TYPE)"
    echo "Session affinity can only be configured on Pool type backends."
    exit 1
fi

# Create updated configuration with session affinity
echo "Creating updated configuration with session affinity..."
UPDATED_CONFIG=$(echo "$CURRENT_CONFIG" | jq '.properties.pool.sessionAffinity = {
    "affinityType": "Cookie",
    "cookieName": "APIM-Backend-Affinity",
    "sessionId": {
        "source": "Cookie",
        "name": "APIM-Backend-Affinity"
    }
}')

# Write the updated configuration to a temporary file
TEMP_FILE=$(mktemp)
echo "$UPDATED_CONFIG" > "$TEMP_FILE"

echo "Updated configuration:"
echo "$UPDATED_CONFIG" | jq '.properties.pool.sessionAffinity'

# Update the backend pool using REST API
echo "Applying session affinity configuration..."
az rest \
    --method PUT \
    --url "$API_URL" \
    --body "@$TEMP_FILE" \
    --headers "If-Match=*"

if [ $? -eq 0 ]; then
    echo "✅ Session affinity enabled successfully!"
    echo "Backend pool '$BACKEND_POOL_ID' now uses cookie-based session affinity with cookie name 'APIM-Backend-Affinity'"
else
    echo "❌ Error: Failed to update backend configuration."
    rm "$TEMP_FILE"
    exit 1
fi

# Clean up
rm "$TEMP_FILE"

# Verify the configuration
echo "Verifying configuration..."
VERIFICATION_URL="/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.ApiManagement/service/$APIM_SERVICE_NAME/backends/$BACKEND_POOL_ID?api-version=2023-05-01-preview"
VERIFICATION=$(az rest \
    --method GET \
    --url "$VERIFICATION_URL" \
    --query "properties.pool.sessionAffinity")

echo "Session affinity configuration:"
echo "$VERIFICATION" | jq '.'

echo "Session affinity configuration complete!"
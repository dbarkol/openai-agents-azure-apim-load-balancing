RESOURCE_GROUP=<resource-group-name>
APIM_SERVICE_NAME=<apim-service-name>
BACKEND_POOL_ID=<backend-pool-name>
SUBSCRIPTION_ID=<azure-subscription-id>

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

echo "🔍 Checking session affinity configuration..."
echo "Resource Group: $RESOURCE_GROUP"
echo "APIM Service: $APIM_SERVICE_NAME"
echo "Backend Pool: $BACKEND_POOL_ID"
echo "Subscription: $SUBSCRIPTION_ID"
echo ""

# Check session affinity configuration
echo "📋 Session Affinity Configuration:"
az rest --method GET \
  --url "https://management.azure.com/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.ApiManagement/service/$APIM_SERVICE_NAME/backends/$BACKEND_POOL_ID?api-version=2023-09-01-preview" \
  --query "properties.pool.sessionAffinity"

echo ""
echo "🔧 Backend Pool Services:"
az rest --method GET \
  --url "https://management.azure.com/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.ApiManagement/service/$APIM_SERVICE_NAME/backends/$BACKEND_POOL_ID?api-version=2023-09-01-preview" \
  --query "properties.pool.services[].id"

echo ""
echo "📊 Complete Backend Pool Configuration:"
az rest --method GET \
  --url "https://management.azure.com/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.ApiManagement/service/$APIM_SERVICE_NAME/backends/$BACKEND_POOL_ID?api-version=2023-09-01-preview" \
  --query "properties.pool"

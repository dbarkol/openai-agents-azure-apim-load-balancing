# Enable Session Affinity for APIM Backend Pool

This guide shows how to enable session affinity on an existing Azure API Management backend pool.

## Prerequisites

- Azure CLI installed and logged in (`az login`)
- jq installed for JSON processing
- Resource group name, APIM service name, and backend pool ID

## Method 1: Azure REST API Script (Recommended)

**Note**: Azure CLI doesn't support `az apim backend` commands, so we use the Azure REST API directly.

Use the provided script to update your existing backend pool:

1. **Update the configuration variables** in `scripts/enable-session-affinity.sh`:
   ```bash
   RESOURCE_GROUP="your-resource-group"
   APIM_SERVICE_NAME="your-apim-service"
   BACKEND_POOL_ID="your-backend-pool-id"
   ```

2. **Make the script executable and run it**:
   ```bash
   chmod +x scripts/enable-session-affinity.sh
   ./scripts/enable-session-affinity.sh
   ```

The script will:
- Use Azure REST API to retrieve your current backend pool configuration
- Add session affinity settings
- Update the backend pool via REST API
- Verify the changes

## Method 2: Manual Azure CLI Commands

If you prefer to run commands manually:

```bash
# Set your variables
RESOURCE_GROUP="your-resource-group"
APIM_SERVICE_NAME="your-apim-service"
BACKEND_POOL_ID="your-backend-pool-id"

# Get current configuration
az apim backend show \
    --resource-group "$RESOURCE_GROUP" \
    --service-name "$APIM_SERVICE_NAME" \
    --backend-id "$BACKEND_POOL_ID" \
    --output json > current-config.json

# Create updated configuration (requires jq)
jq '.pool.sessionAffinity = {
    "affinityType": "Cookie",
    "cookieName": "APIM-Backend-Affinity",
    "sessionId": {
        "source": "Cookie",
        "name": "APIM-Backend-Affinity"
    }
}' current-config.json > updated-config.json

# Apply the update
az apim backend update \
    --resource-group "$RESOURCE_GROUP" \
    --service-name "$APIM_SERVICE_NAME" \
    --backend-id "$BACKEND_POOL_ID" \
    --if-match "*" \
    --set-json @updated-config.json

# Verify
az apim backend show \
    --resource-group "$RESOURCE_GROUP" \
    --service-name "$APIM_SERVICE_NAME" \
    --backend-id "$BACKEND_POOL_ID" \
    --query "pool.sessionAffinity"
```

## Method 3: ARM Template Deployment

Use the ARM template to redeploy your backend pool with session affinity:

```bash
az deployment group create \
    --resource-group "your-resource-group" \
    --template-file templates/backend-pool-session-affinity.json \
    --parameters \
        apimServiceName="your-apim-service" \
        backendPoolId="your-backend-pool-id" \
        backends='[{"url":"https://your-openai-sweden-central.openai.azure.com"},{"url":"https://your-openai-east-us.openai.azure.com"}]'
```

## Method 4: Bicep Template Deployment

Use the Bicep template for type-safe deployment:

```bash
az deployment group create \
    --resource-group "your-resource-group" \
    --template-file templates/backend-pool-session-affinity.bicep \
    --parameters \
        apimServiceName="your-apim-service" \
        backendPoolId="your-backend-pool-id" \
        backends='[{"url":"https://your-openai-sweden-central.openai.azure.com"},{"url":"https://your-openai-east-us.openai.azure.com"}]'
```

## Configuration Details

The session affinity configuration adds this to your backend pool:

```json
{
  "pool": {
    "sessionAffinity": {
      "affinityType": "Cookie",
      "cookieName": "APIM-Backend-Affinity",
      "sessionId": {
        "source": "Cookie",
        "name": "APIM-Backend-Affinity"
      }
    }
  }
}
```

### Session Affinity Options

- **affinityType**: `"Cookie"` (currently the only supported type)
- **cookieName**: Custom cookie name for session tracking (default: `"APIM-Backend-Affinity"`)
- **sessionId**: Required object specifying the source and name for session identification

## Verification

After enabling session affinity, verify it's working:

1. **Check the configuration**:
   ```bash
   az apim backend show \
       --resource-group "your-resource-group" \
       --service-name "your-apim-service" \
       --backend-id "your-backend-pool-id" \
       --query "pool.sessionAffinity"
   ```

2. **Test with your demo script**:
   ```bash
   python src/function-calling-demo.py
   ```

   The output should show consistent backend routing when the session cookie is present.

## Impact on Existing Policies

With native session affinity enabled, you can **simplify your APIM policies**:

- Remove custom session tracking logic from `apim/policies.xml`
- Let APIM handle backend selection automatically
- Keep essential policies like authentication and logging

The native session affinity works alongside your existing policies and should resolve the backend switching issues you experienced with the OpenAI Responses API.

## Troubleshooting

- **Permission errors**: Ensure you have `API Management Service Contributor` role
- **Backend not found**: Verify the backend pool ID matches exactly
- **jq not found**: Install jq with `brew install jq` (macOS) or your package manager
- **API version issues**: The session affinity feature requires API version `2023-05-01-preview` or later
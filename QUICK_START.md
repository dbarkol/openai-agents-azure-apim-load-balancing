# Quick Reference: Enable Session Affinity

## Fastest Method (Azure REST API Script)

**Note**: Azure CLI doesn't support APIM backend commands, so this script uses REST API.

1. Edit `scripts/enable-session-affinity.sh` with your values:
   - `RESOURCE_GROUP`
   - `APIM_SERVICE_NAME` 
   - `BACKEND_POOL_ID`

2. Run: `./scripts/enable-session-affinity.sh`

## Manual Azure REST API (if you prefer step-by-step)

```bash
# Replace with your actual values
RESOURCE_GROUP="your-rg"
APIM_SERVICE_NAME="your-apim"
BACKEND_POOL_ID="your-pool-id"
SUBSCRIPTION_ID=$(az account show --query id --output tsv)

# Get current config using REST API
az rest --method GET \
    --url "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.ApiManagement/service/$APIM_SERVICE_NAME/backends/$BACKEND_POOL_ID?api-version=2023-05-01-preview" \
    > current.json

# Add session affinity (requires jq)
jq '.properties.pool.sessionAffinity = {"affinityType": "Cookie", "cookieName": "APIM-Backend-Affinity", "sessionId": {"source": "Cookie", "name": "APIM-Backend-Affinity"}}' current.json > updated.json

# Apply update using REST API
az rest --method PUT \
    --url "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.ApiManagement/service/$APIM_SERVICE_NAME/backends/$BACKEND_POOL_ID?api-version=2023-05-01-preview" \
    --body @updated.json \
    --headers "If-Match=*"
```

## What This Does

- Adds native session affinity to your existing backend pool
- Uses cookie `APIM-Backend-Affinity` to route requests to same backend
- No more custom routing logic needed in policies
- Fixes the Sweden Central → East US switching issue

## After Setup

Test with: `python src/function-calling-demo.py`

You should see consistent backend routing!
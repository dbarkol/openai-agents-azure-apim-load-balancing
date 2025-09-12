param apimServiceName string
param backendPoolId string
param backends array = [
  {
    url: 'https://your-openai-sweden-central.openai.azure.com'
  }
  {
    url: 'https://your-openai-east-us.openai.azure.com'
  }
]
param cookieName string = 'APIM-Backend-Affinity'

resource apimBackendPool 'Microsoft.ApiManagement/service/backends@2023-05-01-preview' = {
  name: '${apimServiceName}/${backendPoolId}'
  properties: {
    description: 'OpenAI backend pool with session affinity'
    type: 'Pool'
    pool: {
      services: backends
      sessionAffinity: {
        affinityType: 'Cookie'
        cookieName: cookieName
        sessionId: {
          source: 'Cookie'
          name: cookieName
        }
      }
    }
    protocol: 'http'
    url: backends[0].url
  }
}

output backendPoolId string = backendPoolId
output sessionAffinityEnabled bool = true
output cookieName string = cookieName

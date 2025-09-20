import os
import httpx
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

# Custom transport to log cookies and backend info
class CookieLoggingTransport(httpx.HTTPTransport):
    def handle_request(self, request):
        cookies = request.headers.get('cookie', 'None')
        print(f"🍪 Request cookies: {cookies}")
        
        response = super().handle_request(request)
        
        # Log all set-cookie headers
        set_cookies = response.headers.get_list('set-cookie')
        for cookie in set_cookies:
            print(f"🍪 Response set-cookie: {cookie}")

        # Debug headers from APIM policy - same as function-calling-demo.py
        backend_pool = response.headers.get('x-backend-pool', 'unknown')
        request_id = response.headers.get('x-request-id', 'none')
        region = response.headers.get('x-ms-region', 'unknown')
        
        print(f"🌐 Backend: {backend_pool}, Region: {region}, Request: {request_id}")
        print("-" * 50)

        return response

def get_response_text(response):
    """Extract text from the nested response structure"""
    try:
        return response.output[0].content[0].text
    except (IndexError, AttributeError):
        return str(response)[:100] + "..."

inference_api_path = "inference" 
inference_api_version = "2025-03-01-preview"
apim_resource_gateway_url = os.getenv("APIM_GATEWAY_URL") 
api_key = os.getenv("API_KEY") 

print(f"🚀 Testing Azure SDK with session affinity")
print(f"🌐 Gateway: {apim_resource_gateway_url}")
print("=" * 60)

# Create HTTP client with cookie support and custom transport
http_client = httpx.Client(
    transport=CookieLoggingTransport(),
    #cookies=httpx.Cookies()  # Enable cookie jar for session affinity
)

client = AzureOpenAI(
    api_key=api_key,
    base_url=f"{apim_resource_gateway_url}/inference/openai",
    default_query={"api-version": inference_api_version},
    api_version=inference_api_version,
    http_client=http_client  # Pass the cookie-enabled client
)

print("📝 Step 1: Creating initial response...")
response = client.responses.create(
    model='gpt-4.1-mini',
    input="This is a test"
)

print(f"✅ First response ID: {response.id}")
print(f"📄 Content: {get_response_text(response)[:100]}...")
print()

print("📝 Step 2: Creating follow-up response with previous_response_id...")
print("⚠️  This will FAIL if session affinity is broken!")

try:
    second_response = client.responses.create(
        model='gpt-4.1-mini',
        previous_response_id=response.id,
        input=[{"role": "user", "content": "Explain this at a level that could be understood by a college freshman"}]
    )
    
    print(f"✅ Second response ID: {second_response.id}")
    print(f"📄 Content: {get_response_text(second_response)[:100]}...")
    print("\n✅ SUCCESS: Session affinity is working!")
    
except Exception as e:
    print(f"❌ FAILURE: {e}")
    if "not found" in str(e).lower():
        print("💡 This is the expected error when session affinity is broken!")
        print("💡 The previous_response_id exists on a different backend.")

# Clean up
http_client.close()

print("\n" + "=" * 60)
print("🔍 ANALYSIS:")
print("- If you see different regions between requests → session affinity broken")
print("- If you get 'not found' error → previous_response_id is on different backend")
print("- If both requests succeed → session affinity is working")
print("- Check for APIM-Backend-Affinity cookies in the logs above")
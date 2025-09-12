import os
from openai import AsyncOpenAI
import logging
from agents import Agent, Runner, set_default_openai_client, set_tracing_disabled, OpenAIChatCompletionsModel, OpenAIResponsesModel, function_tool, set_default_openai_api
from dotenv import load_dotenv
import httpx

load_dotenv()

# Custom transport to log cookies
# Remove for production - shows what cookies are being sent and received
class CookieLoggingTransport(httpx.AsyncHTTPTransport):
    async def handle_async_request(self, request):
        cookies = request.headers.get('cookie', 'None')
        print(f"Request cookies: {cookies}")
        
        response = await super().handle_async_request(request)
        
        # Log all set-cookie headers (both custom and native session affinity)
        set_cookies = response.headers.get_list('set-cookie')
        for cookie in set_cookies:
            print(f"Response set-cookie: {cookie}")

        # Debug headers from APIM policy
        backend_pool = response.headers.get('x-backend-pool', 'unknown')
        session_id = response.headers.get('x-session-id', 'none')
        request_id = response.headers.get('x-request-id', 'none')
        routing_decision = response.headers.get('x-routing-decision', 'unknown')
        region = response.headers.get('x-ms-region', 'unknown')
        
        print(f"Backend: {backend_pool}, Session: {session_id}, Request: {request_id}")
        print(f"Region: {region}, Routing: {routing_decision}")

        return response

# Enable detailed HTTP logging
# logging.basicConfig(level=logging.DEBUG)
# logging.getLogger("openai").setLevel(logging.DEBUG)
# logging.getLogger("httpx").setLevel(logging.DEBUG)

# Tool 1: Simple Calculator
@function_tool
def add_numbers(a: float, b: float) -> str:
    """Add two numbers together and return the result."""
    result = a + b
    return f"The sum of {a} and {b} is {result}"

# Tool 2: Time/Date Information
@function_tool
def get_current_info() -> str:
    """Get the current date and time information."""
    from datetime import datetime
    now = datetime.now()
    return f"Current date and time: {now.strftime('%Y-%m-%d %H:%M:%S')}"

async def function_call_test():

    azure_base_url = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")

    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")

    # Use async context manager so httpx closes connections cleanly.
    # The cookie jar will automatically handle both SessionBackend and APIM-Backend-Affinity cookies
    async with httpx.AsyncClient(
        transport=CookieLoggingTransport(),
        cookies=httpx.Cookies()  # Enable cookie jar for automatic cookie management
    ) as http_client:

        client = AsyncOpenAI(
            api_key=azure_api_key,
            base_url=azure_base_url,
            default_headers={"api-key": azure_api_key},
            http_client=http_client
        )

        try:
            agent = Agent(
                name="ToolsAgent",
                instructions="Reply succintly, break down each step. Always use the provided tools",
                model=OpenAIResponsesModel(
                    model=deployment,
                    openai_client=client
                ),
                tools=[add_numbers, get_current_info]
            )

            result = await Runner.run(
                agent, "add 2 and 3, and then the result of that to 5. Get the current time"
            )

            print("Response:")
            print(result.final_output)
            
            print("\n=== Session Affinity Test Complete ===")
            print("Expected: Both requests should go to the same region/backend")
            print("If you see different regions, check your APIM policy configuration")

        finally:
            # If the OpenAI client provides an async close, call it to free resources.
            close_fn = getattr(client, "aclose", None)
            if close_fn is not None:
                await close_fn()

if __name__ == "__main__":
    import asyncio
    asyncio.run(function_call_test())

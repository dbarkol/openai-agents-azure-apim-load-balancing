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
        print(f"🍪 Request cookies: {request.headers.get('cookie', 'None')}")
        response = await super().handle_async_request(request)
        set_cookie = response.headers.get('set-cookie')
        if set_cookie:
            print(f"🍪 Response set-cookie: {set_cookie}")
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

    azure_base_url=os.getenv("AZURE_OPENAI_ENDPOINT") 
    azure_api_key=os.getenv("AZURE_OPENAI_API_KEY") 

    # Create HTTP client with cookie jar and logging
    # Essential for session affinity - automatically stores and sends cookies
    # Required for multi-turn conversations
    # Remote 'transport' for production
    http_client = httpx.AsyncClient(
        transport=CookieLoggingTransport(),
        cookies=httpx.Cookies()  # Enable cookie jar
    )

    client = AsyncOpenAI(
        api_key="",
        base_url=azure_base_url,
        default_headers={"api-key": azure_api_key},
        http_client=http_client
    )

    deployment = "gpt-4o-mini"

    agent = Agent(
        name="ToolsAgent",
        instructions="Reply succintly, break down each step. Always use the provided tools",
        model=OpenAIChatCompletionsModel(
            model=deployment,
            openai_client=client
        ),
        tools=[add_numbers, get_current_info]
    )

    #OpenAIResponsesModel
    #OpenAIChatCompletionsModel

    result = await Runner.run(
        agent, "add 2 and 3, and then the result of that to 5. Get the current time"
    )

    print("Response:", result.final_output)

if __name__ == "__main__":
    import asyncio
    asyncio.run(function_call_test())

# OpenAI Agents - Azure APIM Load Balancing

Azure API Management (APIM) load balancing reference for OpenAI Agents. This repository demonstrates a lightweight pattern for multi-region failover, session-aware routing, and function-calling support when using Azure-hosted OpenAI endpoints behind API Management.

Contents

- Quick demo script (`src/function-calling-demo.py`)
- Example APIM policy (`apim/policies.xml`)
- Notes for running locally and behind APIM

Features

- Session affinity: preserves conversation cookies for multi-turn sessions.
- Function calling: sample tool functions and an agent runner demo in `src/function-calling-demo.py`.
- APIM policy example: `apim/policies.xml` shows routing and cookie handling patterns.

Prerequisites

- Python 3.10+ recommended.
- Dependencies: install with `pip install -r requirements.txt`.
- Azure resources: an Azure OpenAI (or Azure OpenAI-compatible) deployment and an API Management instance if you want APIM in front.
- Environment variables: at minimum set `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_API_KEY` (see Quickstart). Optionally set `AZURE_OPENAI_DEPLOYMENT` to choose the deployment (defaults to `gpt-4o-mini`).

Quickstart (local)

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

1. Create a `.env` file in the repo root (or export variables) with at least:

```bash
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_API_KEY=your_api_key_here
```


1. (Optional) To select a non-default model deployment, set `AZURE_OPENAI_DEPLOYMENT` in `.env` or the environment.

1. Run the demo:

```bash
python src/function-calling-demo.py
```

This will run a small agent that demonstrates function calling (simple add and current-time tools) using an `AsyncOpenAI` client configured to use a cookie jar for session affinity. The demo now:

- creates the `httpx.AsyncClient` inside an `async with` block so connections are closed cleanly;
- passes `api_key` to the `AsyncOpenAI` client and also sets the Azure `api-key` header via `default_headers` for authentication;
- selects the model deployment from `AZURE_OPENAI_DEPLOYMENT` (defaults to `gpt-4o-mini`);
- prints the final response on the line after the `Response:` label (see the demo output).

APIM and `apim/policies.xml`

- The `apim/policies.xml` file contains an example APIM inbound/outbound policy that illustrates cookie passthrough and routing hints for load balancing across backend regions. Use it as a starting point for configuring session-aware routing and failover in API Management.
- In production, configure APIM policies to rewrite or inject headers, validate requests, and control which backend region receives traffic.

Security & production notes

- Do not commit secrets. Keep `AZURE_OPENAI_API_KEY` out of source control and prefer managed identities where possible.
- Cookie logging is enabled in the demo via a custom transport for visibility. Remove the `CookieLoggingTransport` and any verbose logging in production.
- APIM: prefer managed identities and secure backend credentials in APIM named values or Azure Key Vault.

Contributing

- Contributions and issues welcome. Open a PR or issue describing the change.

License

- This project is licensed under the terms in `LICENSE`.

Useful files

- `src/function-calling-demo.py`: runnable demo showing session-aware HTTP client, function tools, and an Agent/Runner example.
- `apim/policies.xml`: APIM policy example for cookie/session handling and routing hints.

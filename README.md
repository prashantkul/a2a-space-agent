# Space Explorer A2A Agent

An **Agent-to-Agent (A2A)** enabled Google ADK agent that explores space data using The Space Devs GraphQL API through an authenticated MCP server.

## Overview

This agent demonstrates how to build a production-ready A2A-compatible agent using Google's Agent Development Kit (ADK). It showcases:

- **A2A Protocol Support**: Can be called by other agents via RemoteA2aAgent
- **MCP Integration**: Connects to Model Context Protocol servers for tools
- **OAuth2 Authentication**: Implements Auth0 authentication flow for secure MCP access
- **Standalone & Multi-Agent Operation**: Works independently or as part of agent orchestration

## Features

### Space Exploration Capabilities
- Search for upcoming rocket launches
- Get information about astronauts
- Find out who's currently in space
- Explore celestial bodies and space missions

### A2A Architecture
- Exposes an agent card (`agent.json`) for discovery
- Implements the A2A protocol for agent-to-agent communication
- Can be integrated into multi-agent systems
- Supports both local and remote agent invocation

## Quick Start

### Prerequisites

1. **Python 3.10+**
2. **Google ADK** installed: `pip install google-adk[a2a]`
3. **Auth0 Account** (for MCP authentication)
4. **MCP Server** running (Apollo MCP Server or similar)

### Installation

```bash
# Clone or copy this directory
cd space-agent-a2a

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. **Create/Update `.env` file** in `space_agent_a2a/` directory:

```bash
# Auth0 Configuration
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_CLIENT_ID=your_client_id
AUTH0_CLIENT_SECRET=your_client_secret
AUTH0_API_AUDIENCE=http://your-mcp-server:8000/mcp
ADK_CALLBACK_URL=http://127.0.0.1:8000/dev-ui/

# Google Cloud Configuration (for ADK)
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_REGION=us-central1

# Or use Gemini API Key
GOOGLE_API_KEY=your_gemini_api_key
```

2. **Update MCP Server URL** in `space_agent_a2a/agent.py`:

```python
connection_params=StreamableHTTPConnectionParams(
    url="http://your-mcp-server:8000/mcp",  # Update this URL
    timeout=30.0,
)
```

3. **Update A2A Agent Card URL** in `space_agent_a2a/agent.json`:

```json
{
  "url": "http://localhost:8000/a2a/space_explorer",
  ...
}
```

For production deployment, change to your actual service URL:
```json
{
  "url": "https://your-service.run.app/a2a/space_explorer",
  ...
}
```

## Usage

### Running as a Standalone Agent

```bash
# Run the agent with ADK web UI (port 8000)
adk web space_agent_a2a

# Or run using the main.py entry point
python main.py
```

Access the agent at: `http://127.0.0.1:8000/dev-ui/`

### Running as an A2A Server

```bash
# Start the agent as an A2A server on port 8001
adk api_server --a2a --port 8001 space_agent_a2a
```

The agent card will be available at:
- `http://localhost:8001/a2a/space_explorer/.well-known/agent.json`
- RPC endpoint: `http://localhost:8001/a2a/space_explorer`

### Using as a Remote Agent

In another agent, you can call this space explorer agent:

```python
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH

# Create a reference to the remote space explorer agent
space_agent = RemoteA2aAgent(
    name="space_explorer",
    description="Agent that provides space exploration data",
    agent_card=f"http://localhost:8001/a2a/space_explorer{AGENT_CARD_WELL_KNOWN_PATH}"
)

# Use in your root agent
root_agent = LlmAgent(
    name="orchestrator",
    instruction="You can delegate space-related queries to the space_explorer agent",
    sub_agents=[space_agent],
    ...
)
```

## Architecture

```
┌─────────────────────┐
│  Space Explorer     │
│  Agent (A2A)        │
│                     │
│  ┌───────────────┐  │
│  │ OAuth2 Auth   │  │
│  │ (Auth0)       │  │
│  └───────┬───────┘  │
│          │          │
│  ┌───────▼───────┐  │
│  │ MCP Toolset   │  │
│  │ (Apollo MCP)  │  │
│  └───────┬───────┘  │
│          │          │
│  ┌───────▼───────┐  │
│  │ Space Devs    │  │
│  │ GraphQL API   │  │
│  └───────────────┘  │
└─────────────────────┘
         ▲
         │ A2A Protocol
         │
┌────────┴────────────┐
│  Other Agents       │
│  (RemoteA2aAgent)   │
└─────────────────────┘
```

## Project Structure

```
space-agent-a2a/
├── space_agent_a2a/
│   ├── __init__.py           # Package initialization
│   ├── agent.py              # Main agent definition (root_agent)
│   ├── agent.json            # A2A agent card
│   ├── oauth_helper.py       # OAuth2 authentication helper
│   ├── storage_tool.py       # Conversation storage tool
│   ├── .env                  # Environment configuration (not in git)
│   └── README.md             # Original documentation
├── main.py                   # Entry point for running the agent
├── requirements.txt          # Python dependencies
├── pyproject.toml            # Project metadata and config
└── README.md                 # This file
```

## Key Files

### `agent.json` - A2A Agent Card

Defines the agent's capabilities, skills, and endpoint:

```json
{
  "name": "space_explorer",
  "description": "...",
  "skills": [...],
  "url": "http://localhost:8000/a2a/space_explorer",
  "version": "1.0.0"
}
```

**Important**: Update the `url` field when deploying to different environments.

### `agent.py` - Agent Definition

Exports `root_agent` - the main LlmAgent instance that:
- Configures MCP toolset with OAuth2 authentication
- Defines agent instructions and capabilities
- Implements A2A-compatible interface

### `main.py` - Entry Point

Simple runner for the agent using `run_agent()`:

```python
from space_agent_a2a.agent import root_agent
from google.adk.agent import run_agent

run_agent(root_agent, port=8000)
```

## Customization Guide

### 1. Change Agent Name and Description

Update these locations:
- `agent.json`: `name` and `description` fields
- `agent.py`: `LlmAgent(name="...", description="...")`
- `space_agent_a2a/__init__.py`: Package docstring

### 2. Add New Tools

```python
# In agent.py
def my_custom_tool(param: str) -> str:
    """Tool description."""
    return f"Result for {param}"

root_agent = LlmAgent(
    ...
    tools=[get_mcp_toolset(), save_conversation, my_custom_tool],
)
```

### 3. Modify Agent Instructions

Edit the `instruction` parameter in `agent.py`:

```python
root_agent = LlmAgent(
    ...
    instruction="""Your custom instructions here...""",
)
```

### 4. Add Skills to Agent Card

Update `agent.json`:

```json
{
  "skills": [
    {
      "id": "new_skill",
      "name": "New Skill Name",
      "description": "What this skill does",
      "tags": ["tag1", "tag2"]
    }
  ]
}
```

### 5. Change MCP Server

Update the `get_mcp_toolset()` function in `agent.py`:

```python
def get_mcp_toolset():
    return McpToolset(
        connection_params=StreamableHTTPConnectionParams(
            url="http://your-new-mcp-server:8000/mcp",
            timeout=30.0,
        ),
        ...
    )
```

## Deployment

### Local Development

```bash
# Terminal 1: Run as A2A server
adk api_server --a2a --port 8001 space_agent_a2a

# Terminal 2: Run another agent that calls this one
adk web your_orchestrator_agent
```

### Cloud Run (Google Cloud)

1. **Update `agent.json`** with your Cloud Run URL:

```json
{
  "url": "https://space-explorer-xyz.run.app/a2a/space_explorer"
}
```

2. **Deploy**:

```bash
gcloud run deploy space-explorer \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars AUTH0_DOMAIN=...,AUTH0_CLIENT_ID=...
```

3. **Use from other agents**:

```python
space_agent = RemoteA2aAgent(
    name="space_explorer",
    description="Remote space exploration agent",
    agent_card="https://space-explorer-xyz.run.app/a2a/space_explorer/.well-known/agent.json"
)
```

### Agent Engine (Vertex AI)

Follow Google's ADK documentation for deploying to Agent Engine:
- Ensure all tools are serializable (avoid `errlog` parameters)
- Configure appropriate service accounts
- Set environment variables in the Agent Engine config

## Example Interactions

### Standalone Mode

```
User: What are the next 3 upcoming rocket launches?
Agent: [Uses space tools to fetch and display launch information]
```

### A2A Mode (Called by Orchestrator)

```python
# In orchestrator agent
orchestrator = LlmAgent(
    instruction="""
    When users ask about space, delegate to space_explorer.
    When users ask about weather, delegate to weather_agent.
    """,
    sub_agents=[space_agent, weather_agent]
)
```

```
User: Tell me about the next SpaceX launch
Orchestrator: [Delegates to space_explorer]
Space Explorer: [Returns launch information]
Orchestrator: [Presents results to user]
```

## Troubleshooting

### A2A Connection Issues

1. **Verify agent card URL**:
   ```bash
   curl http://localhost:8001/a2a/space_explorer/.well-known/agent.json
   ```

2. **Check if A2A server is running**:
   ```bash
   ps aux | grep "adk api_server"
   ```

3. **Verify the `url` field in `agent.json` matches your deployment**

### MCP Authentication Errors

1. **Check Auth0 configuration** in `.env`
2. **Verify MCP server is accessible**:
   ```bash
   curl http://your-mcp-server:8000/mcp
   ```
3. **Check OAuth2 scopes** match MCP server requirements

### Agent Not Responding

1. **Check ADK logs** for errors
2. **Verify environment variables** are set correctly
3. **Test tools individually** before running full agent
4. **Ensure model has quota** (Gemini API key or GCP project)

## Best Practices

1. **Environment Variables**: Never commit `.env` files - use `.gitignore`
2. **Agent Card URLs**: Always update `agent.json` URL for each deployment environment
3. **Tool Design**: Keep tools focused and well-documented
4. **Error Handling**: Implement proper error handling in custom tools
5. **Testing**: Test both standalone and A2A modes
6. **Security**: Use proper authentication for production deployments

## Resources

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [A2A Protocol Specification](https://github.com/google/adk-python/blob/main/AGENTS.md)
- [MCP Documentation](https://modelcontextprotocol.io/)
- [The Space Devs API](https://thespacedevs.com/)

## License

Apache License 2.0

## Contributing

This is a starter template. Customize it for your needs and share improvements with the community!

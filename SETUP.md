# Setup Guide - Space Explorer A2A Agent

Complete setup instructions for configuring and running the Space Explorer A2A agent.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the Agent](#running-the-agent)
5. [Testing A2A Functionality](#testing-a2a-functionality)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

- **Python 3.10 or higher**
  ```bash
  python --version  # Should show 3.10+
  ```

- **pip** (Python package manager)
  ```bash
  pip --version
  ```

- **Google Cloud SDK** (optional, for GCP deployment)
  ```bash
  gcloud --version
  ```

### Required Accounts

1. **Google Cloud Account** or **Gemini API Key**
   - Option A: [Get a Gemini API Key](https://ai.google.dev/gemini-api/docs/api-key)
   - Option B: [Create GCP Project](https://console.cloud.google.com/)

2. **Auth0 Account** (for MCP authentication)
   - [Sign up for Auth0](https://auth0.com/signup)
   - Create a new application (type: Regular Web Application)

3. **MCP Server** (Apollo MCP Server or similar)
   - Must be running and accessible
   - Should support The Space Devs API

## Installation

### Step 1: Clone or Download

```bash
# If you received this as a git repository
git clone <repository-url>
cd space-agent-a2a

# Or if you have the files directly
cd space-agent-a2a
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Install from requirements.txt
pip install -r requirements.txt

# Or install with development dependencies
pip install -e ".[dev]"
```

### Step 4: Verify Installation

```bash
# Check ADK installation
adk --version

# Verify Python imports
python -c "from google.adk import Agent; print('ADK installed successfully')"
```

## Configuration

### Step 1: Auth0 Setup

1. **Log in to Auth0 Dashboard**
   - Go to https://manage.auth0.com/

2. **Create a New Application**
   - Click "Applications" → "Create Application"
   - Name: "Space Explorer Agent"
   - Type: "Regular Web Application"
   - Click "Create"

3. **Configure Application Settings**
   - Go to application "Settings" tab
   - Note down:
     - Domain (e.g., `dev-xxxxx.us.auth0.com`)
     - Client ID
     - Client Secret

4. **Set Allowed Callback URLs**
   ```
   http://127.0.0.1:8000/dev-ui/,
   http://localhost:8000/dev-ui/
   ```

5. **Set Allowed Logout URLs**
   ```
   http://127.0.0.1:8000/dev-ui/,
   http://localhost:8000/dev-ui/
   ```

6. **Create API** (if not already created)
   - Click "APIs" → "Create API"
   - Name: "MCP Server API"
   - Identifier: `http://your-mcp-server:8000/mcp` (your MCP server URL)
   - Signing Algorithm: RS256

7. **Configure API Permissions**
   - In your API, add scopes: `read:users`, `openid`, `profile`, `email`

### Step 2: Environment Variables

1. **Copy the example .env file**
   ```bash
   cp space_agent_a2a/.env.example space_agent_a2a/.env
   ```

2. **Edit `space_agent_a2a/.env`** with your credentials:

   ```bash
   # Auth0 Configuration
   AUTH0_DOMAIN=dev-xxxxx.us.auth0.com
   AUTH0_CLIENT_ID=your_client_id_here
   AUTH0_CLIENT_SECRET=your_client_secret_here
   AUTH0_API_AUDIENCE=http://your-mcp-server:8000/mcp
   ADK_CALLBACK_URL=http://127.0.0.1:8000/dev-ui/

   # Google Cloud Configuration
   GOOGLE_CLOUD_PROJECT=your-project-id
   GOOGLE_CLOUD_REGION=us-central1

   # Or use Gemini API Key (easier for local development)
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

### Step 3: Update MCP Server URL

Edit `space_agent_a2a/agent.py` and update the MCP server URL:

```python
def get_mcp_toolset():
    return McpToolset(
        connection_params=StreamableHTTPConnectionParams(
            url="http://34.61.171.198:8000/mcp",  # Change to your MCP server
            timeout=30.0,
        ),
        ...
    )
```

### Step 4: Verify Configuration

```bash
# Check that .env file is present
ls -la space_agent_a2a/.env

# Test environment variable loading
python -c "
from dotenv import load_dotenv
import os
load_dotenv('space_agent_a2a/.env')
print('Auth0 Domain:', os.getenv('AUTH0_DOMAIN'))
print('MCP Server:', os.getenv('AUTH0_API_AUDIENCE'))
"
```

## Running the Agent

### Mode 1: Standalone Agent (Web UI)

```bash
# Run with ADK web command (recommended)
adk web space_agent_a2a

# Or run using main.py
python main.py
```

Access at: **http://127.0.0.1:8000/dev-ui/**

### Mode 2: A2A Server

```bash
# Start as A2A server on port 8001
adk api_server --a2a --port 8001 space_agent_a2a
```

Verify it's running:
```bash
# Check agent card
curl http://localhost:8001/a2a/space_explorer/.well-known/agent.json

# Should return JSON with agent information
```

### Mode 3: Both Modes (Two Terminals)

**Terminal 1 - A2A Server:**
```bash
adk api_server --a2a --port 8001 space_agent_a2a
```

**Terminal 2 - Orchestrator Agent:**
```bash
adk web examples/
```

Now you can interact with the orchestrator at `http://127.0.0.1:8000/dev-ui/`, which will delegate space queries to the A2A server.

## Testing A2A Functionality

### Test 1: Verify Agent Card

```bash
# Get the agent card
curl http://localhost:8001/a2a/space_explorer/.well-known/agent.json | jq

# Expected output:
# {
#   "name": "space_explorer",
#   "description": "...",
#   "skills": [...],
#   "url": "http://localhost:8001/a2a/space_explorer",
#   ...
# }
```

### Test 2: Run Example Orchestrator

1. **Start the Space Explorer A2A server** (Terminal 1):
   ```bash
   adk api_server --a2a --port 8001 space_agent_a2a
   ```

2. **Start the orchestrator agent** (Terminal 2):
   ```bash
   adk web examples/
   ```

3. **Test queries** in the web UI (http://127.0.0.1:8000/dev-ui/):
   - "Greet me as Alice" → Should use local greeter agent
   - "What are the next SpaceX launches?" → Should delegate to remote space_explorer
   - Check the logs in Terminal 1 to see A2A requests

### Test 3: Verify Tool Execution

In the web UI, try these queries:

```
1. "What are the next 3 rocket launches?"
2. "Tell me about astronauts currently in space"
3. "Find information about Mars missions"
```

You should see:
- OAuth2 authentication flow (if first time)
- MCP tool execution
- Formatted responses with space data

## Troubleshooting

### Issue: "Missing required Auth0 environment variables"

**Solution:**
1. Check `.env` file exists: `ls space_agent_a2a/.env`
2. Verify all variables are set (no empty values)
3. Restart the agent after updating `.env`

### Issue: Agent card returns 404

**Solution:**
1. Verify A2A server is running: `ps aux | grep "adk api_server"`
2. Check correct port: `8001` by default
3. Verify URL in browser: `http://localhost:8001/a2a/space_explorer/.well-known/agent.json`

### Issue: OAuth2 authentication fails

**Solution:**
1. **Check Auth0 configuration**:
   - Verify callback URLs include `http://127.0.0.1:8000/dev-ui/`
   - Ensure API audience matches MCP server URL
2. **Clear browser cache** and try again
3. **Check Auth0 logs** in dashboard for error details

### Issue: MCP connection timeout

**Solution:**
1. **Verify MCP server is running**:
   ```bash
   curl http://your-mcp-server:8000/mcp
   ```
2. **Check firewall/network** settings
3. **Increase timeout** in `agent.py`:
   ```python
   timeout=60.0  # Increase from 30.0
   ```

### Issue: RemoteA2aAgent can't connect

**Solution:**
1. **Verify agent card URL** is correct in `orchestrator_agent.py`
2. **Check logs** of A2A server (Terminal 1)
3. **Ensure agent.json URL** matches deployment:
   ```json
   {
     "url": "http://localhost:8001/a2a/space_explorer"
   }
   ```

### Issue: Import errors

**Solution:**
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Verify google-adk installation with a2a extras
pip show google-adk
# Should show version >= 0.1.0

# Check a2a-sdk is installed
pip list | grep a2a-sdk
```

### Issue: Agent not using tools

**Solution:**
1. **Check tool registration** in `agent.py`:
   ```python
   tools=[get_mcp_toolset(), save_conversation]
   ```
2. **Verify MCP toolset initialization**:
   ```python
   # Test in Python console
   from space_agent_a2a.agent import get_mcp_toolset
   toolset = get_mcp_toolset()
   print(toolset)
   ```
3. **Check agent instructions** mention when to use tools

## Next Steps

After successful setup:

1. **Customize the agent** for your use case
2. **Add more tools** or sub-agents
3. **Deploy to production** (Cloud Run, Agent Engine)
4. **Build an orchestrator** that uses multiple A2A agents

## Additional Resources

- [ADK Documentation](https://google.github.io/adk-docs/)
- [A2A Protocol Guide](https://github.com/google/adk-python/blob/main/AGENTS.md)
- [Auth0 Quickstarts](https://auth0.com/docs/quickstarts)
- [MCP Documentation](https://modelcontextprotocol.io/)

## Getting Help

If you encounter issues not covered here:

1. **Check ADK samples**: `contributing/samples/a2a_*` in the ADK repository
2. **Review logs**: Look for error messages in terminal output
3. **Test components individually**: MCP server, Auth0, agent card
4. **Consult ADK documentation**: https://google.github.io/adk-docs/

---

**Ready to build?** Start with `adk web space_agent_a2a` and explore the agent!

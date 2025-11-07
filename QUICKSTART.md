# Quick Start - 5 Minutes to A2A Agent

Get the Space Explorer A2A agent running in 5 minutes.

## Prerequisites

- Python 3.10+
- [Gemini API Key](https://ai.google.dev/gemini-api/docs/api-key)
- MCP Server URL (Apollo MCP or similar)
- Auth0 account (for MCP authentication)

## Step 1: Install (30 seconds)

```bash
cd space-agent-a2a
pip install -r requirements.txt
```

## Step 2: Configure (2 minutes)

### Create `.env` file

```bash
cp space_agent_a2a/.env.example space_agent_a2a/.env
```

### Edit `space_agent_a2a/.env`

```bash
# Required: Your Gemini API key
GOOGLE_API_KEY=YOUR_GEMINI_API_KEY_HERE

# Required: Auth0 credentials
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_CLIENT_ID=your_client_id
AUTH0_CLIENT_SECRET=your_client_secret
AUTH0_API_AUDIENCE=http://your-mcp-server:8000/mcp

# Optional but recommended
ADK_CALLBACK_URL=http://127.0.0.1:8000/dev-ui/
```

### Update MCP Server URL

Edit `space_agent_a2a/agent.py` (line ~112):

```python
url="http://YOUR_MCP_SERVER:8000/mcp",  # Change this
```

## Step 3: Run (30 seconds)

### Option A: Standalone Agent

```bash
adk web space_agent_a2a
```

Open: http://127.0.0.1:8000/dev-ui/

### Option B: A2A Server

```bash
adk api_server --a2a --port 8001 space_agent_a2a
```

Test: http://localhost:8001/a2a/space_explorer/.well-known/agent.json

### Option C: Full A2A Demo (Two Terminals)

**Terminal 1:**
```bash
adk api_server --a2a --port 8001 space_agent_a2a
```

**Terminal 2:**
```bash
adk web examples/
```

Open: http://127.0.0.1:8000/dev-ui/

## Step 4: Test (1 minute)

Try these queries in the web UI:

```
1. "What are the next rocket launches?"
2. "Who is currently in space?"
3. "Tell me about Mars missions"
```

For A2A testing (when using orchestrator):

```
1. "Greet me as Alice"  (uses local agent)
2. "What are the next SpaceX launches?"  (uses remote A2A agent)
```

## Common Issues

### "Missing environment variables"
→ Check `space_agent_a2a/.env` has all required values

### Agent card 404
→ Ensure A2A server is running: `ps aux | grep "adk api_server"`

### MCP connection fails
→ Verify MCP server URL in `agent.py` and `.env` file

### OAuth errors
→ Check Auth0 callback URLs include `http://127.0.0.1:8000/dev-ui/`

## What's Next?

✅ **Working?** Great! Now read [README.md](README.md) for customization
✅ **Issues?** See [SETUP.md](SETUP.md) for detailed troubleshooting
✅ **Deploy?** Check README section on Cloud Run deployment

## Architecture Summary

```
Your Orchestrator → RemoteA2aAgent → Space Explorer (A2A Server)
                                    ↓
                                MCP Toolset (OAuth2)
                                    ↓
                                Apollo MCP Server
                                    ↓
                                Space Devs API
```

## Key Files

- **`space_agent_a2a/agent.py`** - Main agent definition
- **`space_agent_a2a/agent.json`** - A2A agent card
- **`space_agent_a2a/.env`** - Your configuration
- **`examples/orchestrator_agent.py`** - Example using RemoteA2aAgent
- **`main.py`** - Simple runner script

## Commands Cheat Sheet

```bash
# Run standalone
adk web space_agent_a2a

# Run as A2A server
adk api_server --a2a --port 8001 space_agent_a2a

# Run example orchestrator
adk web examples/

# Check agent card
curl http://localhost:8001/a2a/space_explorer/.well-known/agent.json

# Test with custom port
adk web --port 9000 space_agent_a2a
```

---

**Stuck?** Check [SETUP.md](SETUP.md) for detailed instructions.
**Want more?** Read [README.md](README.md) for full documentation.

"""Space Explorer Agent - Uses Apollo MCP Server to explore space data.

OAuth approach (based on ADK sample pattern):
- Auth0 authorization code grant flow for user authentication
- Anonymous MCP server discovery (initialize, tools/list)
- User tokens for tool execution (true user-level authorization)
- ADK-managed credential lifecycle via oauth_helper
- Automatic token refresh with offline_access scope
"""

import os
from typing import Union
from google.adk.agents import LlmAgent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.auth.auth_credential import AuthCredential, AuthCredentialTypes, OAuth2Auth
from google.adk.auth.auth_schemes import ExtendedOAuth2
from google.adk.auth.auth_tool import AuthConfig
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.adk.tools.tool_context import ToolContext
from fastapi.openapi.models import OAuthFlowAuthorizationCode, OAuthFlows

# from .oauth_helper import get_user_credentials  # Temporarily commented
from .storage_tool import save_conversation
from .mcp_wrapper import McpToolsetWrapper


# load environment variables from .env file
from dotenv import load_dotenv

load_dotenv()


# Auth0 configuration from environment variables (.env file)
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
API_AUDIENCE = os.getenv("AUTH0_API_AUDIENCE")
REDIRECT_URI = os.getenv("ADK_CALLBACK_URL", "http://127.0.0.1:8081/dev-ui/")

# Validate required environment variables at runtime
# Note: This validation happens when the agent is instantiated, not at import time.
# For starter template purposes, we warn but don't fail on import.
_env_vars_configured = all([AUTH0_DOMAIN, CLIENT_ID, CLIENT_SECRET, API_AUDIENCE])
if not _env_vars_configured:
    import warnings
    warnings.warn(
        "Auth0 environment variables not fully configured. "
        "Please set AUTH0_DOMAIN, AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET, "
        "AUTH0_API_AUDIENCE in space_agent_a2a/.env before running the agent. "
        "Copy .env.example to .env and fill in your credentials.",
        UserWarning
    )

SCOPES = ["read:users", "openid", "profile", "email", "offline_access"]
CREDENTIAL_CACHE_KEY = "auth0_mcp_credential"


# Configure OAuth2 auth scheme for Auth0 with authorization code flow
auth_scheme = ExtendedOAuth2(
    flows=OAuthFlows(
        authorizationCode=OAuthFlowAuthorizationCode(
            authorizationUrl=f"https://{AUTH0_DOMAIN}/authorize",
            tokenUrl=f"https://{AUTH0_DOMAIN}/oauth/token",
            scopes={scope: scope for scope in SCOPES},
        )
    ),
    issuer_url=f"https://{AUTH0_DOMAIN}",
)

# Configure OAuth2 credentials with audience
auth_credential = AuthCredential(
    auth_type=AuthCredentialTypes.OAUTH2,
    oauth2=OAuth2Auth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        audience=API_AUDIENCE,
        redirect_uri=REDIRECT_URI,
    ),
)

# Create MCP toolset with user authentication
# - MCP server allows anonymous discovery (initialize, tools/list)
# - auth_scheme/credential: User authentication via OAuth2 authorization code flow
#   (user tokens reach the MCP server for tool execution - true user-level authorization!)
#
# Authentication flow:
# 1. Tool discovery (initialize, tools/list) - anonymous, no auth required
# 2. Tool execution (tools/call) - requires user OAuth token from auth_scheme
# 3. MCP server validates user token and can enforce per-user permissions


def get_mcp_toolset():
    """Create and return the MCP toolset on demand."""
    return McpToolset(
        connection_params=StreamableHTTPConnectionParams(
            url="http://34.61.171.198:8000/mcp",
            timeout=30.0,  # Increased timeout for better stability
        ),
        auth_scheme=auth_scheme,
        auth_credential=auth_credential,
        tool_name_prefix="space",
        errlog=None,  # Avoid pickle errors during Agent Engine deployment
    )


# Define the root agent
# This agent is A2A-compatible and can:
# 1. Be called by other agents via RemoteA2aAgent
# 2. Serve its capabilities through the A2A protocol
# 3. Work as a standalone agent through the ADK web UI
root_agent = LlmAgent(
    name="space_explorer",
    model="gemini-2.5-flash",
    instruction="""You are a space exploration assistant with access to The Space Devs API. You are an A2A-enabled agent that can be called by other agents.

You can help users with:
- Finding information about upcoming rocket launches
- Learning about astronauts and who's currently in space
- Exploring information about celestial bodies and space missions
- Answering space-related questions with accurate, real-time data

When answering questions:
1. Use the available space tools to get accurate, real-time data
2. Provide detailed and engaging responses about space exploration
3. If asked about current launches or astronauts, always use the tools to get the latest information
4. Be enthusiastic about space exploration!

As an A2A-enabled agent, you can:
- Respond to requests from other agents
- Provide space data to orchestrator agents
- Work as part of a multi-agent system

Available tools allow you to:
- Search for upcoming launches
- Get details about astronauts
- Find out who's currently in space
- Explore celestial bodies and space objects
""",
    description="An AI agent that explores space data using The Space Devs GraphQL API through an authenticated MCP server",
    tools=[
        get_mcp_toolset(),  
        save_conversation,
    ],
)

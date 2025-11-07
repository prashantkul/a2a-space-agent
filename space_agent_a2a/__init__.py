"""Space Explorer A2A Agent.

This package contains an A2A-enabled Google ADK agent that explores space data
using The Space Devs GraphQL API through an authenticated MCP server.

The agent can be:
1. Run as a standalone agent via the ADK web UI
2. Called by other agents via the A2A protocol
3. Deployed as a remote A2A service
"""

from .agent import root_agent

__all__ = ["root_agent"]

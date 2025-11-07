"""MCP Toolset Wrapper to fix Pydantic serialization issues for A2A.

This wrapper prevents the MCP ClientSession from being serialized by Pydantic,
which causes issues with the A2A server's OpenAPI generation.
"""

from typing import Any, Optional, Dict, List
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.adk.auth.auth_credential import AuthCredential
from google.adk.auth.auth_schemes import ExtendedOAuth2
from pydantic import BaseModel, Field, ConfigDict


class McpToolsetWrapper(BaseModel):
    """Wrapper for McpToolset that is Pydantic-compatible.

    This wrapper stores the configuration needed to create an McpToolset
    but doesn't store the actual McpToolset instance, avoiding serialization issues.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    connection_url: str = Field(description="MCP server URL")
    timeout: float = Field(default=30.0, description="Connection timeout")
    tool_name_prefix: str = Field(default="space", description="Prefix for tool names")
    # Using __pydantic_private__ prefix to exclude from serialization
    __pydantic_private__ = {
        '_toolset': None,
        '_auth_scheme': None,
        '_auth_credential': None,
    }

    def __init__(
        self,
        connection_url: str,
        auth_scheme: Optional[ExtendedOAuth2] = None,
        auth_credential: Optional[AuthCredential] = None,
        timeout: float = 30.0,
        tool_name_prefix: str = "space",
        **data
    ):
        super().__init__(
            connection_url=connection_url,
            timeout=timeout,
            tool_name_prefix=tool_name_prefix,
            **data
        )
        # Store in private attributes that are excluded from serialization
        self.__pydantic_private__['_auth_scheme'] = auth_scheme
        self.__pydantic_private__['_auth_credential'] = auth_credential
        self.__pydantic_private__['_toolset'] = None

    def get_toolset(self) -> McpToolset:
        """Get or create the actual McpToolset instance."""
        if self.__pydantic_private__['_toolset'] is None:
            self.__pydantic_private__['_toolset'] = McpToolset(
                connection_params=StreamableHTTPConnectionParams(
                    url=self.connection_url,
                    timeout=self.timeout,
                ),
                auth_scheme=self.__pydantic_private__['_auth_scheme'],
                auth_credential=self.__pydantic_private__['_auth_credential'],
                tool_name_prefix=self.tool_name_prefix,
                errlog=None,  # Avoid serialization issues
            )
        return self.__pydantic_private__['_toolset']

    # Delegate tool methods to the actual toolset
    async def __call__(self, *args, **kwargs):
        """Make the wrapper callable like the actual toolset."""
        toolset = self.get_toolset()
        return await toolset(*args, **kwargs)

    def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools from the MCP server."""
        toolset = self.get_toolset()
        return toolset.list_tools()

    def __getattr__(self, name):
        """Delegate attribute access to the actual toolset."""
        if name.startswith('_'):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        toolset = self.get_toolset()
        return getattr(toolset, name)
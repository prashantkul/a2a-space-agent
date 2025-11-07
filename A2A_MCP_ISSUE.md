# A2A Server MCP Compatibility Issue

## Problem Summary
The Google ADK A2A server fails to start when using MCP (Model Context Protocol) tools due to a Pydantic schema generation error. The MCP library's `ClientSession` class doesn't implement the necessary Pydantic schema generation methods required by ADK's FastAPI-based A2A server.

## Error Details
```
PydanticSchemaGenerationError: Unable to generate pydantic-core schema for <class 'mcp.client.session.ClientSession'>
```

This error occurs when the A2A server attempts to generate OpenAPI documentation, which is required for A2A endpoints to function.

## Root Cause
1. ADK's A2A server uses FastAPI, which requires Pydantic schemas for OpenAPI generation
2. MCP's `ClientSession` class doesn't implement `__get_pydantic_core_schema__`
3. Without successful OpenAPI generation, A2A endpoints (including agent card) aren't created

## Attempted Solutions

### 1. MCP Wrapper with Private Fields
Created `McpToolsetWrapper` class using `__pydantic_private__` to exclude MCP internals from serialization.
**Result**: Partial success - server starts but MCP internals still leak through during schema generation.

### 2. FastAPI/Pydantic Downgrade
As suggested in [GitHub Issue #3173](https://github.com/google/adk-python/issues/3173#issuecomment-3444660877):
- Downgraded to `fastapi==0.118.3`
- Kept `pydantic>=2.11.1,<3`
**Result**: No improvement - issue persists with older versions.

### 3. Specific Version Combination
Tested with:
- `mcp==1.12.0`
- `pydantic==2.10.6`
- `fastapi==0.118.3`
**Result**: OpenAPI generation works but A2A endpoints still not created. The --a2a flag appears to be incompatible with MCP tools regardless of versions.

## Current Status
- **With ADK 1.16.0 + specific package versions**: Server starts without PydanticSchemaGenerationError but A2A endpoints are NOT created
- **Agent card endpoint (/.well-known/agent-card.json)**: Returns 404 even without MCP tools
- **Issue persists with ADK 1.16.0**: The --a2a flag appears to not properly create A2A endpoints in this version

## Workarounds

### Option 1: Remove MCP Tools for A2A Testing
Comment out MCP tools from the agent definition when testing A2A functionality:
```python
root_agent = LlmAgent(
    name="space_explorer",
    model="gemini-2.5-flash",
    instruction="...",
    tools=[
        # get_mcp_toolset(),  # Comment out for A2A testing
        save_conversation
    ],
)
```

### Option 2: Wait for Library Updates
The issue requires either:
1. MCP library to add Pydantic support to `ClientSession`
2. ADK to handle non-Pydantic-compatible tools gracefully

### Option 3: Custom Tool Implementation
Replace MCP with a custom implementation that's fully Pydantic-compatible.

## Known Limitations
1. **A2A Incompatibility**: Cannot use MCP tools with A2A server
2. **No Agent Discovery**: Without A2A, agent cannot be discovered or called by other agents
3. **Limited Integration**: Cannot participate in multi-agent systems

## Related Issues
- [Google ADK Issue #3173](https://github.com/google/adk-python/issues/3173) - MCP Pydantic serialization
- [Google ADK Issue #1055](https://github.com/google/adk-python/issues/1055) - Unable to use MCP tools
- [MCP SDK Issue #1060](https://github.com/modelcontextprotocol/python-sdk/issues/1060) - PydanticSchemaGenerationError

## Recommendation
For production use with A2A requirements, consider:
1. Using alternative tool implementations that are Pydantic-compatible
2. Implementing a proxy service that wraps MCP functionality without exposing MCP internals
3. Waiting for official fix from either MCP or ADK teams

## Testing
To verify if the issue is resolved in future versions:
```bash
# Start A2A server
adk api_server --a2a --port 8000 space_agent_a2a

# Test agent card endpoint
curl http://localhost:8000/.well-known/agent-card.json
```

Success criteria: Agent card JSON should be returned without 404 error.
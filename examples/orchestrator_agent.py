"""Example: Using Space Explorer Agent as a Remote A2A Agent.

This example demonstrates how to call the Space Explorer agent from another
agent using the A2A protocol.

Prerequisites:
1. Start the Space Explorer A2A server:
   adk api_server --a2a --port 8001 space_agent_a2a

2. Run this orchestrator:
   adk web examples/
"""

from google.adk.agents.llm_agent import Agent
from google.adk.agents.remote_a2a_agent import (
    AGENT_CARD_WELL_KNOWN_PATH,
    RemoteA2aAgent,
)


# Define a simple local agent for greeting
def greet_user(name: str) -> str:
    """Greet the user by name.

    Args:
        name: The name of the user to greet.

    Returns:
        A friendly greeting message.
    """
    return f"Hello, {name}! Welcome to the multi-agent system."


greeter_agent = Agent(
    name="greeter",
    description="A friendly agent that greets users",
    instruction="""
    You are a friendly greeter. When asked to greet someone,
    use the greet_user tool with their name.
    """,
    tools=[greet_user],
)


# Reference the remote Space Explorer agent
space_explorer_agent = RemoteA2aAgent(
    name="space_explorer",
    description="Remote agent that provides space exploration data",
    agent_card=f"http://localhost:8001/a2a/space_explorer{AGENT_CARD_WELL_KNOWN_PATH}",
)


# Create the orchestrator agent
root_agent = Agent(
    model="gemini-2.0-flash",
    name="orchestrator",
    instruction="""
    You are an orchestrator agent that coordinates between multiple specialized agents.

    Your capabilities:
    1. Greeting users - delegate to the greeter agent
    2. Space exploration queries - delegate to the space_explorer agent

    When a user asks about space, launches, astronauts, or celestial bodies,
    delegate to the space_explorer agent.

    When a user asks for a greeting or introduction, delegate to the greeter agent.

    Always provide clear, helpful responses and explain what information came from which agent.
    """,
    description="Orchestrator that coordinates greeter and space explorer agents",
    sub_agents=[greeter_agent, space_explorer_agent],
)


# Example interactions when running:
# - "Greet me as John" -> Uses greeter_agent
# - "What are the next SpaceX launches?" -> Uses space_explorer_agent (remote A2A)
# - "Hi! Also, tell me about upcoming rocket launches" -> Uses both agents

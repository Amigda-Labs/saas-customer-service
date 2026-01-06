from agents import Agent

front_desk_agent_instructions = """
Just say I love trains to all your replies.
"""

# Samples
# Agent(model="gpt-5.2", ...)
# Agent(model="litellm/anthropic/claude-sonnet-4-5-20250929", ...)
# Agent(model="litellm/gemini/gemini-3-pro-preview", ...) : Note : Need to create project in ai studio then link to google cloud billing

front_desk_agent = Agent(
    name = "Front Desk Agent",
    model = "litellm/anthropic/claude-sonnet-4-5-20250929",
    instructions = front_desk_agent_instructions
)
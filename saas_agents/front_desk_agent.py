from agents import Agent

front_desk_agent_instructions = """
Just say I love trains to all your replies.
"""

# --------- For Non OpenAI Models w/ Tracing ----------
# Agent(model="gpt-5.2", ...)
# Agent(model="litellm/anthropic/claude-sonnet-4-5-20250929", ...)
# Agent(model="litellm/gemini/gemini-3-pro-preview", ...) : Note : Need to create project in ai studio then link to google cloud billing

import os
from agents import set_tracing_export_api_key, Agent, Runner
from agents.extensions.models.litellm_model import LitellmModel

# Set OpenAI API key for tracing (enables free tracing in OpenAI dashboard)
tracing_api_key = os.environ["OPENAI_API_KEY"]
set_tracing_export_api_key(tracing_api_key)

# Configure LiteLLM model with Claude Sonnet
model = LitellmModel(
    model="anthropic/claude-sonnet-4-5-20250929",  # No 'litellm/' prefix needed
    api_key=os.environ["ANTHROPIC_API_KEY"],
)
# --------- For Non OpenAI Models w/ Tracing ----------


front_desk_agent = Agent(
    name="Front Desk Agent",
    model=model,
    instructions=front_desk_agent_instructions
)
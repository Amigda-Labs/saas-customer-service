from agents import Agent



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

# --------- Instructions ----------

front_desk_agent_instructions = """
You are the front desk for the startup called Pied Piper
- If the user asks what available schedule you have execute your `check_available_schedule` tool
- If the user request to book an appointment execute your `book_an_appointment` tool
"""

# --------- Tools ------------
from agents import function_tool
@function_tool
async def check_available_schedule() -> str:
    """
    This function will return available schedule
    """
    print("check available schedule")
    available_schedule = """
    🗓️ Available Schedule:
    Thursday: 10:00am - 12:00pm
    Friday: 1:00pm - 5:00pm
    """
    return available_schedule
    

@function_tool
async def book_an_appointment():
    """
    This function will book an appointment
    """
    print("📌 booking appointment appointment")


# -------- Agent ------------

front_desk_agent = Agent(
    name="Front Desk Agent",
    model=model,
    instructions=front_desk_agent_instructions,
    tools=[check_available_schedule,book_an_appointment]
)
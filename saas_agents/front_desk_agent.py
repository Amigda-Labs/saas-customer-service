from datetime import date
from typing import Any


from agents import Agent, RunContextWrapper
from core.context import SharedContext


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
    
from agents import RunContextWrapper
from core.context import SharedContext
from datetime import datetime

@function_tool
async def book_an_appointment(
    ctx: RunContextWrapper[SharedContext],
    name: str,
    contact_num: str,
    start_time: datetime,
    end_time: datetime
) -> str :
    """
    Book an appointment with the provided details.
    
    Args:
        name: Customer's full name
        contact_num: Customer's contact number  
        start_time: Appointment start time
        end_time: Appointment end time
    """
    # Access the context via ctx.context
    ctx.context.name = name
    ctx.context.contact_num = contact_num
    ctx.context.start_time = start_time
    ctx.context.end_time = end_time

    print("📌 booking appointment appointment")
    return f"✅ Appointment booked for {name} from {start_time} to {end_time}"


# -------- Agent ------------

front_desk_agent = Agent[SharedContext](
    name="Front Desk Agent",
    model=model,
    instructions=front_desk_agent_instructions,
    tools=[check_available_schedule,book_an_appointment]
)
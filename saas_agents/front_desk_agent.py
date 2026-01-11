"""
Front Desk Agent for handling customer inquiries and appointments.

This agent can:
- Check available schedule from Google Calendar
- Book appointments for customers
"""

import os
from datetime import datetime

from agents import Agent, RunContextWrapper, function_tool
from agents import set_tracing_export_api_key
from agents.extensions.models.litellm_model import LitellmModel

from core.context import SharedContext
from services.google_calendar import get_available_schedule, create_calendar_event

from guardrails.input.booking_abuse import booking_abuse_guardrail

# --------- For Non OpenAI Models w/ Tracing ----------
# Agent(model="gpt-5.2", ...)
# Agent(model="litellm/anthropic/claude-sonnet-4-5-20250929", ...)
# Agent(model="litellm/gemini/gemini-3-pro-preview", ...) : Note : Need to create project in ai studio then link to google cloud billing

# Set OpenAI API key for tracing (enables free tracing in OpenAI dashboard)
tracing_api_key = os.environ["OPENAI_API_KEY"]
set_tracing_export_api_key(tracing_api_key)

# Configure LiteLLM model with Claude Sonnet
model = LitellmModel(
    model="anthropic/claude-sonnet-4-5-20250929",  # No 'litellm/' prefix needed
    api_key=os.environ["ANTHROPIC_API_KEY"],
)

# --------- Instructions ----------

def get_front_desk_instructions() -> str:
    """Generate instructions with current date context."""
    current_date = datetime.now().strftime("%A, %B %d, %Y")
    current_year = datetime.now().year
    
    return f"""You are the front desk for the startup called Pied Piper.

IMPORTANT: Today's date is {current_date}. The current year is {current_year}.
When booking appointments, ALWAYS use the year {current_year} unless the user specifically requests a different year.

Your responsibilities:
- If the user asks what available schedule you have, execute your `check_available_schedule` tool
- If the user requests to book an appointment, execute your `book_an_appointment` tool
- When the user provides a date without a year, assume they mean {current_year}
- Never book appointments in the past
"""

front_desk_agent_instructions = get_front_desk_instructions()

# --------- Tools ------------

@function_tool
async def check_available_schedule() -> str:
    """
    Check available schedule by querying Google Calendar.
    Returns available time slots for the next 7 business days.
    """
    print("📅 Checking available schedule from Google Calendar...")
    
    try:
        return get_available_schedule()
    except FileNotFoundError:
        return "❌ Error: credentials.json not found. Please set up Google Calendar API credentials."
    except Exception as e:
        print(f"Error checking calendar: {e}")
        return f"❌ Error checking calendar availability: {str(e)}"


@function_tool
async def book_an_appointment(
    ctx: RunContextWrapper[SharedContext],
    name: str,
    contact_num: str,
    start_time: datetime,
    end_time: datetime
) -> str:
    """
    Book an appointment with the provided details.
    
    Args:
        name: Customer's full name
        contact_num: Customer's contact number  
        start_time: Appointment start time
        end_time: Appointment end time
    """
    print("📌 Booking appointment...")
    
    try:
        # Store in context
        ctx.context.name = name
        ctx.context.contact_num = contact_num
        ctx.context.start_time = start_time
        ctx.context.end_time = end_time
        
        # Create event in Google Calendar
        event = create_calendar_event(
            summary=f"Appointment: {name}",
            description=f"Customer: {name}\nContact: {contact_num}",
            start_time=start_time,
            end_time=end_time
        )
        
        event_link = event.get('htmlLink', '')
        return f"✅ Appointment booked for {name} from {start_time} to {end_time}\n📎 Calendar link: {event_link}"
        
    except FileNotFoundError:
        return "❌ Error: credentials.json not found. Please set up Google Calendar API credentials."
    except Exception as e:
        print(f"Error booking appointment: {e}")
        return f"❌ Error booking appointment: {str(e)}"


# -------- Agent ------------

front_desk_agent = Agent[SharedContext](
    name="Front Desk Agent",
    model=model,
    #model="gpt-5.2",
    instructions=front_desk_agent_instructions,
    tools=[check_available_schedule, book_an_appointment],
    input_guardrails=[booking_abuse_guardrail],
)

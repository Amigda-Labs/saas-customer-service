"""
Booking abuse guardrail to prevent denial-of-service attacks.

Detects users attempting to:
- Book all available slots
- Mass book appointments to block others
- Spam booking requests
"""

from pydantic import BaseModel
from agents import (
    Agent,
    GuardrailFunctionOutput,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
)

#Create Input Guardrail Structure Result
class BookingAbuseAnalysis(BaseModel):
    """Output schema for booking abuse detection."""
    is_abuse_attempt: bool
    reasoning: str
    threat_level: str  # "none", "low", "medium", "high"
    abuse_type: str | None  # e.g., "mass_booking", "slot_hoarding", "spam", None

#Agent
booking_abuse_detector_instructions = """

You are a security filter for a scheduling system at Pied Piper.
Analyze the user's message to detect potential booking abuse or denial-of-service attempts.

FLAG AS ABUSE (is_abuse_attempt = True) if the user:
- Asks to book ALL available slots or times
- Requests multiple appointments in a single message (more than 2)
- Expresses intent to "fill up", "block", or "reserve everything"
- Wants to book on behalf of fake/multiple people to hoard slots
- Shows patterns of trying to exhaust availability
- Uses language suggesting malicious intent ("book everything so no one else can")

Examples of ABUSE:
- "Book me for every slot you have available"
- "I want to reserve all your openings for next week"
- "Schedule appointments for John, Jane, Jim, Jake, and Jerry all tomorrow"
- "Can you block out your entire calendar for me?"
- "I need 10 appointments"

NOT ABUSE (is_abuse_attempt = False):
- Normal single appointment booking
- Asking about availability (just checking)
- Booking 1-2 appointments for legitimate reasons
- Rescheduling an existing appointment
- "Book me for 2pm tomorrow" (single booking)
- "Can I also add a follow-up next week?" (reasonable follow-up)

When in doubt about edge cases (e.g., booking 2-3 appointments), set threat_level 
to "low" or "medium" but is_abuse_attempt to False - let them proceed but flag it.

Be reasonable - some users legitimately need 2 appointments. Focus on obvious abuse patterns.
"""

from guardrails.utils.input_extraction import extract_latest_user_message


@input_guardrail(run_in_parallel=False)  # BLOCK before booking tool executes
async def booking_abuse_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    """
    Detect and block booking abuse attempts.
    
    Uses blocking execution (run_in_parallel=False) to prevent
    the booking tool from executing if abuse is detected.
    """

    latest_message = extract_latest_user_message(input)

    result = await Runner.run(booking_abuse_detector, latest_message)
    
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_abuse_attempt,
    )

# Fast guardrail agent to detect abuse
booking_abuse_detector = Agent(
    name="Booking Abuse Detector",
    model="gpt-4o",
    instructions=booking_abuse_detector_instructions,
    output_type=BookingAbuseAnalysis,
)


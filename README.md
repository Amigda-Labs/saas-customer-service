# SaaS Customer Service Agent

An AI-powered front desk agent built with OpenAI Agents that handles customer inquiries and appointment bookings through natural language conversation. The agent integrates with Google Calendar to manage schedules and includes built-in security guardrails to prevent booking abuse.

## 🎯 Features

- **Natural Language Booking**: Customers can book appointments using conversational language
- **Google Calendar Integration**: Real-time schedule checking and appointment creation
- **Smart Guardrails**: Prevents booking abuse and denial-of-service attacks
- **Context Preservation**: Maintains conversation state across multiple interactions
- **Session Management**: SQLite-based session storage for conversation history
- **Multi-Model Support**: Works with OpenAI GPT-5.2, Claude Sonnet 4.5, and other LiteLLM-compatible models
- **Tracing & Observability**: Built-in tracing for debugging and monitoring

## 🏗️ Architecture

```
saas-customer-service/
├── core/                          # Application core
│   ├── main.py                    # Entry point with Runner setup
│   └── context.py                 # Shared context for booking data
├── saas_agents/                   # Agent definitions
│   └── front_desk_agent.py        # Front desk agent with tools
├── services/                      # External service integrations
│   └── google_calendar.py         # Google Calendar API wrapper
├── guardrails/                    # Security and validation
│   └── input/
│       └── booking_abuse.py       # Prevents booking abuse attempts
├── scripts/                       # Utility scripts
│   ├── verify_calendar_auth.py    # Test Google Calendar authentication
│   └── verify_calendar_add_event.py  # Test event creation
└── docs/                          # Documentation
    ├── GOOGLE_CALENDAR_SETUP.md   # Step-by-step Google Calendar setup
    └── ENHANCEMENT_SUGGESTIONS.md # Future feature ideas
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended) or pip
- A Google Cloud account with Calendar API access
- OpenAI API key (for tracing) or Anthropic API key (for Claude model)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd saas-customer-service
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```
   
   Or with pip:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Google Calendar API**
   
   Follow the comprehensive guide in [`docs/GOOGLE_CALENDAR_SETUP.md`](docs/GOOGLE_CALENDAR_SETUP.md) to:
   - Create a Google Cloud project
   - Enable Google Calendar API
   - Configure OAuth consent screen
   - Download `credentials.json`
   - Complete first-time authorization

4. **Configure environment variables**
   
   Create a `.env` file in the project root:
   ```env
   # Required for tracing (even if using Claude)
   OPENAI_API_KEY=sk-your-openai-api-key
   
   # Required if using Claude Sonnet model
   ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key
   ```

5. **Verify Google Calendar setup**
   ```bash
   uv run scripts/verify_calendar_auth.py
   ```
   
   This will:
   - Open a browser for Google OAuth authorization
   - Create `token.json` for future API calls
   - List your upcoming calendar events

### Running the Agent

```bash
uv run -m core.main
```

The agent will start in interactive mode. You can now chat with it:

```
Ask anything: What appointments are available this week?
Ask anything: Book me for tomorrow at 2pm
Ask anything: quit
```

## 🛠️ How It Works

### 1. Front Desk Agent

The agent (`saas_agents/front_desk_agent.py`) uses two primary tools:

- **`check_available_schedule()`**: Queries Google Calendar for available time slots
- **`book_an_appointment()`**: Creates calendar events with customer details

### 2. Business Rules

- **Business Hours**: 9:00 AM - 5:00 PM (configurable in `services/google_calendar.py`)
- **Timezone**: Asia/Manila (configurable)
- **Availability Window**: Next 7 business days (weekends excluded)
- **Year Handling**: Automatically corrects past years to current/next year

### 3. Security Guardrails

The `booking_abuse_guardrail` monitors for malicious patterns:

- Attempting to book all available slots (3+ times)
- Mass booking requests (multiple appointments in one message)
- Intent to block the calendar for others
- Suspicious language patterns

**Threat Levels**:
- `none`: Normal request, proceed
- `low/medium`: Suspicious but allowed (logged)
- `high`: Blocked with explanation to user

### 4. Session Management

Uses SQLite-based sessions to:
- Preserve conversation history across runs
- Enable context-aware responses
- Track user behavior for guardrail detection

## 🔧 Configuration

### Switching AI Models

**OpenAI GPT-5.2** (default in some configurations):
```python
front_desk_agent = Agent[SharedContext](
    model="gpt-5.2",
    # ... other config
)
```

**Claude Sonnet 4.5** (current configuration):
```python
from agents.extensions.models.litellm_model import LitellmModel

model = LitellmModel(
    model="anthropic/claude-sonnet-4-5-20250929",
    api_key=os.environ["ANTHROPIC_API_KEY"],
)

front_desk_agent = Agent[SharedContext](
    model=model,
    # ... other config
)
```

### Customizing Business Hours

Edit `services/google_calendar.py`:
```python
BUSINESS_HOURS_START = 9   # 9 AM
BUSINESS_HOURS_END = 17    # 5 PM
TIMEZONE = 'Asia/Manila'
DAYS_TO_CHECK = 7  # Days ahead to show availability
```

### Adjusting Guardrail Sensitivity

Edit `guardrails/input/booking_abuse.py`:
```python
# Disable blocking (monitor only mode)
return GuardrailFunctionOutput(
    output_info=result.final_output,
    tripwire_triggered=False,  # Change to False
)
```

## 📊 Tracing & Observability

The application includes built-in tracing for monitoring agent behavior:

```python
config = RunConfig(
    trace_include_sensitive_data=True,  # Include full message content
    # tracing_disabled=True,  # Uncomment to disable tracing
    workflow_name="Front Desk Agent Workflow"
)
```

Traces are automatically exported to OpenAI's dashboard (requires `OPENAI_API_KEY`).

## 🧪 Testing

### Test Calendar Authentication
```bash
uv run scripts/verify_calendar_auth.py
```

### Test Event Creation
```bash
uv run scripts/verify_calendar_add_event.py
```

## 🔒 Security Best Practices

1. **Never commit credentials**:
   - `credentials.json` (Google OAuth client secret)
   - `.env` (API keys)

2. **Guardrails are in "block" mode by default**:
   - High-threat abuse attempts are automatically blocked
   - Suspicious activity is logged for review

3. **Use test users during development**:
   - Add your email as a test user in Google Cloud Console
   - Keep OAuth consent screen in "Testing" mode

## 📚 Documentation

- **[Google Calendar Setup Guide](docs/GOOGLE_CALENDAR_SETUP.md)**: Complete walkthrough with screenshots
- **[Enhancement Suggestions](docs/ENHANCEMENT_SUGGESTIONS.md)**: Future feature ideas and improvement opportunities

## 🎨 Example Conversations

**Checking availability:**
```
User: What times do you have available this week?
Agent: 📅 Checking available schedule from Google Calendar...

🗓️ Available Schedule:

📅 Monday, January 13:
   • 09:00 AM - 12:00 PM
   • 02:00 PM - 05:00 PM

📅 Tuesday, January 14:
   • 09:00 AM - 05:00 PM
```

**Booking an appointment:**
```
User: Book me for Tuesday at 2pm, my name is John Doe and my number is 555-1234
Agent: 📌 Booking appointment...
✅ Appointment booked for John Doe from 2025-01-14 14:00:00 to 2025-01-14 15:00:00
📎 Calendar link: https://calendar.google.com/event?eid=...
```

**Guardrail blocking abuse:**
```
User: Book me for every single time slot you have available
Agent: 🚫 Request blocked by security guardrail!
   Reason: User attempting to book all available slots to hoard the calendar
   Threat level: high
   Type: slot_hoarding

Please make a reasonable booking request.
```

## 🚧 Known Limitations

- **No rescheduling**: Cannot move existing appointments
- **No cancellations**: Cannot delete appointments via agent
- **No recurring bookings**: Single appointments only
- **No multi-language support**: English only
- **No payment integration**: Free booking system

See [`docs/ENHANCEMENT_SUGGESTIONS.md`](docs/ENHANCEMENT_SUGGESTIONS.md) for planned improvements.

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional guardrails (time zone validation, duplicate booking detection)
- Support for cancellation and rescheduling
- Multi-language support
- Payment integration
- Webhook notifications

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built with:
- [OpenAI Agents](https://github.com/openai/openai-agents-python) - Agentic framework
- [Google Calendar API](https://developers.google.com/calendar) - Calendar integration
- [LiteLLM](https://github.com/BerriAI/litellm) - Multi-model support
- [Pydantic](https://docs.pydantic.dev/) - Data validation

---

**Project maintained by**: [Your name/organization]

For questions or issues, please open an issue on GitHub.

"""
Google Calendar service for managing appointments and availability.

This module provides functions to:
- Authenticate with Google Calendar API
- Check available time slots
- Create calendar events for bookings
"""

import os
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# --------- Configuration ----------
SCOPES = ['https://www.googleapis.com/auth/calendar.events']
BUSINESS_HOURS_START = 9   # 9 AM
BUSINESS_HOURS_END = 17    # 5 PM
TIMEZONE = 'Asia/Manila'
DAYS_TO_CHECK = 7  # Check availability for next 7 days


def get_calendar_service():
    """
    Create and return an authorized Google Calendar API service.
    
    Returns:
        Google Calendar API service object
        
    Raises:
        FileNotFoundError: If credentials.json is not found
    """
    creds = None
    
    # Check if token.json exists (previous authorization)
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If no valid credentials, start OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    # Build and return the service
    service = build('calendar', 'v3', credentials=creds)
    return service


def _get_busy_times(service, start_date: datetime, end_date: datetime) -> list[tuple[datetime, datetime]]:
    """
    Fetch all events from the calendar and return busy time periods.
    
    Args:
        service: Google Calendar API service
        start_date: Start of the time range to check
        end_date: End of the time range to check
    
    Returns:
        List of tuples containing (start_time, end_time) for each busy period
    """
    events_result = service.events().list(
        calendarId='primary',
        timeMin=start_date.isoformat() + 'Z',
        timeMax=end_date.isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    busy_times = []
    
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        
        # Parse datetime strings
        if 'T' in start:  # DateTime format
            start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
            # Convert to naive datetime for comparison
            start_dt = start_dt.replace(tzinfo=None)
            end_dt = end_dt.replace(tzinfo=None)
        else:  # All-day event
            start_dt = datetime.strptime(start, '%Y-%m-%d')
            end_dt = datetime.strptime(end, '%Y-%m-%d')
        
        busy_times.append((start_dt, end_dt))
    
    return busy_times


def _calculate_available_slots(
    busy_times: list[tuple[datetime, datetime]], 
    start_date: datetime, 
    days: int
) -> dict[str, list[str]]:
    """
    Calculate available time slots based on business hours and busy periods.
    
    Args:
        busy_times: List of (start, end) tuples for busy periods
        start_date: Start date to check availability
        days: Number of days to check
    
    Returns:
        Dictionary mapping date strings to lists of available time slots
    """
    available_slots = {}
    
    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)
        
        # Skip weekends
        if current_date.weekday() >= 5:
            continue
        
        date_str = current_date.strftime('%A, %B %d')
        day_start = current_date.replace(hour=BUSINESS_HOURS_START, minute=0, second=0, microsecond=0)
        day_end = current_date.replace(hour=BUSINESS_HOURS_END, minute=0, second=0, microsecond=0)
        
        # Get busy times for this day
        day_busy = [(s, e) for s, e in busy_times 
                    if s.date() == current_date.date() or e.date() == current_date.date()]
        
        # Sort by start time
        day_busy.sort(key=lambda x: x[0])
        
        # Find available slots
        slots = []
        current_time = day_start
        
        for busy_start, busy_end in day_busy:
            # Clamp busy times to business hours
            busy_start = max(busy_start, day_start)
            busy_end = min(busy_end, day_end)
            
            if busy_start > current_time:
                # There's a free slot before this busy period
                slots.append(f"{current_time.strftime('%I:%M %p')} - {busy_start.strftime('%I:%M %p')}")
            
            current_time = max(current_time, busy_end)
        
        # Check if there's time after the last busy period
        if current_time < day_end:
            slots.append(f"{current_time.strftime('%I:%M %p')} - {day_end.strftime('%I:%M %p')}")
        
        if slots:
            available_slots[date_str] = slots
    
    return available_slots


def _format_availability(available_slots: dict[str, list[str]]) -> str:
    """Format available slots into a readable string."""
    if not available_slots:
        return "❌ No available slots found for the next week."
    
    lines = ["🗓️ Available Schedule:\n"]
    for date_str, slots in available_slots.items():
        lines.append(f"📅 {date_str}:")
        for slot in slots:
            lines.append(f"   • {slot}")
        lines.append("")
    
    return "\n".join(lines)


def get_available_schedule(days: int = DAYS_TO_CHECK) -> str:
    """
    Get available schedule from Google Calendar.
    
    This is the main public function for checking availability.
    It handles authentication, fetches busy times, calculates available slots,
    and returns a formatted string.
    
    Args:
        days: Number of days to check (default: DAYS_TO_CHECK)
    
    Returns:
        Formatted string with available time slots
        
    Raises:
        FileNotFoundError: If credentials.json is not found
        Exception: For other calendar API errors
    """
    # Get the calendar service
    service = get_calendar_service()
    
    # Define the time range to check
    now = datetime.now()
    start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(days=days)
    
    # Fetch busy times from calendar
    busy_times = _get_busy_times(service, start_date, end_date)
    
    # Calculate available slots
    available_slots = _calculate_available_slots(busy_times, start_date, days)
    
    # Format and return the availability
    return _format_availability(available_slots)


def validate_and_fix_datetime(dt: datetime) -> datetime:
    """
    Validate and fix a datetime to ensure it's not in the past.
    
    If the datetime has a year in the past, it assumes the user meant the current
    year (or next year if that date has already passed).
    
    Args:
        dt: The datetime to validate and fix
        
    Returns:
        A valid datetime that is not in the past
        
    Raises:
        ValueError: If the datetime is in the past even after year correction
    """

    # Strip timezone if present (normalize to naive datetime)
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)
        
    now = datetime.now()
    
    # If the year is in the past, try to fix it
    if dt.year < now.year:
        # Replace with current year
        corrected_dt = dt.replace(year=now.year)
        
        # If that date has already passed this year, use next year
        if corrected_dt < now:
            corrected_dt = dt.replace(year=now.year + 1)
        
        print(f"📅 Auto-corrected year: {dt} → {corrected_dt}")
        dt = corrected_dt
    
    # Final check: ensure the datetime is not in the past
    if dt < now:
        raise ValueError(f"Cannot book appointments in the past. Requested time: {dt}, Current time: {now}")
    
    return dt


def create_calendar_event(
    summary: str,
    description: str,
    start_time: datetime,
    end_time: datetime,
    attendee_email: str = None
) -> dict:
    """
    Create a calendar event.
    
    Args:
        summary: Event title
        description: Event description
        start_time: Event start datetime
        end_time: Event end datetime
        attendee_email: Optional email for attendee
    
    Returns:
        Created event object from Google Calendar API
        
    Raises:
        FileNotFoundError: If credentials.json is not found
        ValueError: If the appointment time is in the past
        Exception: For calendar API errors
    """
    # Validate and fix datetimes
    start_time = validate_and_fix_datetime(start_time)
    end_time = validate_and_fix_datetime(end_time)
    
    # Ensure end time is after start time
    if end_time <= start_time:
        raise ValueError(f"End time ({end_time}) must be after start time ({start_time})")
    
    service = get_calendar_service()
    
    event = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': TIMEZONE,
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': TIMEZONE,
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                {'method': 'popup', 'minutes': 30},       # 30 min before
            ],
        },
    }
    
    # Add attendee if provided
    if attendee_email:
        event['attendees'] = [{'email': attendee_email}]
    
    created_event = service.events().insert(
        calendarId='primary',
        body=event,
        sendUpdates='all' if attendee_email else 'none'
    ).execute()
    
    return created_event

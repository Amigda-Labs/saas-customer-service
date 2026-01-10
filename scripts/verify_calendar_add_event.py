"""
Verification script for adding events to Google Calendar.
Tests the ability to create, verify, and optionally delete calendar events.

Usage:
    uv run python scripts/verify_calendar_add_event.py           # Create and keep event
    uv run python scripts/verify_calendar_add_event.py --cleanup # Create, verify, then delete
"""
import os
import argparse
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying scopes, delete token.json
SCOPES = ['https://www.googleapis.com/auth/calendar.events']


def get_calendar_service():
    """Create and return an authorized Calendar API service."""
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


def create_event(service, summary: str, description: str, start_time: datetime, 
                 end_time: datetime, attendee_email: str = None) -> dict:
    """
    Create a calendar event.
    
    Args:
        service: Google Calendar API service
        summary: Event title
        description: Event description
        start_time: Event start datetime
        end_time: Event end datetime
        attendee_email: Optional email for attendee
    
    Returns:
        Created event object
    """
    event = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'America/Mexico_City',  # Adjust to your timezone
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'America/Mexico_City',
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


def delete_event(service, event_id: str) -> bool:
    """Delete a calendar event by ID."""
    try:
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        return True
    except Exception as e:
        print(f"Error deleting event: {e}")
        return False


def get_event(service, event_id: str) -> dict:
    """Get a calendar event by ID."""
    return service.events().get(calendarId='primary', eventId=event_id).execute()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Verify Google Calendar event creation')
    parser.add_argument('--cleanup', action='store_true', 
                        help='Delete the test event after verification')
    parser.add_argument('--title', type=str, default='Test Appointment - SaaS Customer Service',
                        help='Event title')
    parser.add_argument('--duration', type=int, default=60,
                        help='Event duration in minutes (default: 60)')
    args = parser.parse_args()
    
    print("🔐 Getting calendar service...")
    service = get_calendar_service()
    
    # Create a test event for tomorrow
    tomorrow = datetime.now() + timedelta(days=1)
    start_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(minutes=args.duration)
    
    print("\n📅 Creating test event...")
    print(f"   Title: {args.title}")
    print(f"   Start: {start_time}")
    print(f"   End:   {end_time}")
    
    try:
        event = create_event(
            service=service,
            summary=args.title,
            description="This is a test event created by the verification script.\n\nCustomer: Test User\nPhone: +52 123 456 7890",
            start_time=start_time,
            end_time=end_time
        )
        
        print(f"\n✅ Event created successfully!")
        print(f"   Event ID: {event['id']}")
        print(f"   Link: {event.get('htmlLink', 'N/A')}")
        
        # Verify the event was created by fetching it
        print("\n🔍 Verifying event exists...")
        fetched_event = get_event(service, event['id'])
        print(f"   ✅ Event verified: {fetched_event['summary']}")
        
        # Cleanup if requested
        print("\n" + "="*50)
        if args.cleanup:
            print("🗑️  Cleanup requested - deleting test event...")
            if delete_event(service, event['id']):
                print("   ✅ Test event deleted successfully!")
            else:
                print("   ❌ Failed to delete event")
        else:
            print(f"📌 Event kept. View it at:\n   {event.get('htmlLink', 'your calendar')}")
            print("\n💡 Tip: Run with --cleanup to auto-delete test events")
        
        print("\n" + "="*50)
        print("🎉 Calendar event creation verification complete!")
        
    except Exception as e:
        print(f"\n❌ Error creating event: {e}")
        raise

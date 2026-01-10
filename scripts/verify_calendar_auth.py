import os
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

if __name__ == '__main__':
    print("🔐 Starting authorization flow...")
    service = get_calendar_service()
    
    # Test: List next 5 events
    print("\n📅 Testing Calendar API - Fetching upcoming events...")
    events_result = service.events().list(
        calendarId='primary',
        maxResults=10,
        singleEvents=True,
        orderBy='startTime',
        timeMin='2026-01-01T00:00:00Z'
    ).execute()
    
    events = events_result.get('items', [])
    
    if not events:
        print('No upcoming events found.')
    else:
        print(f'Found {len(events)} events:')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f"  - {start}: {event['summary']}")
    
    print("\n✅ Authorization successful! token.json has been created.")

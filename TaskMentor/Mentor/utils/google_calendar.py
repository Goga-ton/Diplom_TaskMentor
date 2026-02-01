from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from django.conf import settings
from datetime import datetime, timedelta
from ..models import GoogleCalendarToken
from django.utils import timezone
from datetime import timedelta

def get_calendar_service(user):
    try:
        token = GoogleCalendarToken.objects.get(user=user)
        creds = Credentials(
            token=token.access_token,
            refresh_token=token.refresh_token,
            token_uri='https://oauth2.googleapis.com/token',
            client_id='dummy_client_id',  # Временно для dummy token
            client_secret='dummy_secret',
            # client_id=settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['client_id'],  # Из Allauth
            # client_secret=settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['secret'],
            scopes=['https://www.googleapis.com/auth/calendar'],
        )
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            token.access_token = creds.token
            token.token_expiry = datetime.now() + timedelta(hours=1)
            token.save()
        return build('calendar', 'v3', credentials=creds)
    except GoogleCalendarToken.DoesNotExist:
        return None

def create_calendar_event(service, task):
    if hasattr(task.due_date, 'isoformat'):
        due_dt = task.due_date
    else:
        due_dt = timezone.make_aware(
            timezone.datetime.fromisoformat(str(task.due_date))
        )

    event = {
        'summary': task.title,
        'description': task.description or '',
        'start': {'dateTime': due_dt.isoformat(), 'timeZone': 'Europe/Moscow'},  # ✅ due_dt
        'end': {'dateTime': (due_dt + timedelta(minutes=30)).isoformat(), 'timeZone': 'Europe/Moscow'},  # ✅ due_dt
        'reminders': {'useDefault': False, 'overrides': [{'method': 'popup', 'minutes': 30}]},
    }
    return service.events().insert(calendarId='primary', body=event).execute()

def sync_task_to_calendar(user, task):
    service = get_calendar_service(user)
    if service:
        event = create_calendar_event(service, task)
        task.calendar_event_id = event['id']
        task.save()
        return event  # ✅ Для print в views
    return None
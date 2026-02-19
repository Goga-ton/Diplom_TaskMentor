from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from datetime import timedelta
from zoneinfo import ZoneInfo
import os
from dotenv import load_dotenv
from ..models import GoogleCalendarToken

#Для выключения и включения флага при отладке параметр задается в settings в DEBUG_CALENDAR_SYNC
from django.conf import settings
def calendar_debug(*args):
    if getattr(settings, "DEBUG_CALENDAR_SYNC", False):
        print(*args)

load_dotenv()

def get_calendar_service(user):
    """
    Возвращает Google Calendar service для user (teacher), используя сохранённые токены.
    При необходимости обновляет access_token через refresh_token.
    """
    try:
        token_row = GoogleCalendarToken.objects.get(user=user)

        creds = Credentials(
            token=token_row.access_token,
            refresh_token=token_row.refresh_token or None,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.getenv("GOOGLE_CLIENT_ID"),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
            scopes=["https://www.googleapis.com/auth/calendar"],
        )

        # Обновление токена, если истёк
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            token_row.access_token = creds.token
            token_row.token_expiry = timezone.now() + timedelta(hours=1)
            token_row.save(update_fields=["access_token", "token_expiry"])

        return build("calendar", "v3", credentials=creds)

    except GoogleCalendarToken.DoesNotExist:
        return None


def _task_to_event_body(task):
    """
    Приводим due_date к aware datetime и собираем event body.
    """
    due_dt = task.due_date

    if isinstance(due_dt, str):
        due_dt = parse_datetime(due_dt) or timezone.datetime.fromisoformat(due_dt)

    MOSCOW_TZ = ZoneInfo("Europe/Moscow")

    if timezone.is_naive(due_dt):
        due_dt = timezone.make_aware(due_dt, MOSCOW_TZ)
    else:
        due_dt = due_dt.astimezone(MOSCOW_TZ)

    tz = "Europe/Moscow"

    calendar_debug("DEBUG due_dt:", due_dt, "tzinfo:", due_dt.tzinfo)
    calendar_debug("DEBUG EVENT BODY:", {
        "start": {"dateTime": due_dt.isoformat(), "timeZone": tz},
        "end": {"dateTime": (due_dt + timedelta(minutes=30)).isoformat(), "timeZone": tz},},)

    return {
        "summary": task.title or "TaskMentor",
        "description": task.description or "",
        "start": {"dateTime": due_dt.isoformat(), "timeZone": tz},
        "end": {"dateTime": (due_dt + timedelta(minutes=30)).isoformat(), "timeZone": tz},
        "reminders": {
            "useDefault": False,
            "overrides": [{"method": "popup", "minutes": 30}],
        },
    }


def upsert_calendar_event(service, task, event_id: str | None = None):
    """
    Если у задачи уже есть calendar_event_id — обновляем событие.
    Если нет — создаём новое и возвращаем.
    """
    body = _task_to_event_body(task)

    if event_id:
        # UPDATE
        return service.events().update(
            calendarId="primary",
            eventId=event_id,
            body=body,
        ).execute()

    # CREATE
    return service.events().insert(
        calendarId="primary",
        body=body
    ).execute()


def delete_calendar_event(service, event_id: str) -> bool:
    """
    Удаляет событие из календаря. Возвращает True если удалили/его уже нет.
    """
    if not event_id:
        return True
    try:
        service.events().delete(calendarId="primary", eventId=event_id).execute()
        return True
    except HttpError as e:
        # Если уже удалено (404) — считаем успехом
        if getattr(e, "status_code", None) == 404:
            return True
        return False


def sync_task_to_calendar(user, task, event_attr: str):
    """
    Upsert события в календарь user.
    event_attr: 'teacher_calendar_event_id' или 'student_calendar_event_id'
    """
    service = get_calendar_service(user)
    if not service:
        calendar_debug("🔍 SYNC: No calendar service for user")
        return None

    try:
        current_event_id = getattr(task, event_attr, None)
        event = upsert_calendar_event(service, task, current_event_id)

        if event and event.get("id") and not current_event_id:
            setattr(task, event_attr, event["id"])
            task.save(update_fields=[event_attr])
            calendar_debug(f"✅ SYNC({event_attr}): Event upserted, id={event.get('id')}")
        return event

    except Exception as e:
        calendar_debug(f"❌ SYNC ERROR: {type(e).__name__}: {e}")
        return None


def remove_task_from_calendar(user, task,  event_attr: str) -> bool:
    """
    Удаляет event по task.calendar_event_id и чистит поле в задаче.
    """
    event_id = getattr(task, event_attr, None)
    if not event_id:
        return True

    service = get_calendar_service(user)
    if not service:
        return False

    ok = delete_calendar_event(service, event_id)
    if ok:
        setattr(task, event_attr, None)
        task.save(update_fields=[event_attr])
        calendar_debug(f"🗑️ SYNC({event_attr}): Event deleted and cleared")
    return ok

def sync_task_for_teacher(teacher, task):
    return sync_task_to_calendar(teacher, task, "teacher_calendar_event_id")

def sync_task_for_student(student, task):
    return sync_task_to_calendar(student, task, "student_calendar_event_id")

def remove_task_for_teacher(teacher, task):
    return remove_task_from_calendar(teacher, task, "teacher_calendar_event_id")

def remove_task_for_student(student, task):
    return remove_task_from_calendar(student, task, "student_calendar_event_id")

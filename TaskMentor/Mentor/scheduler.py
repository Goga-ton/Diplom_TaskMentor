from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
import json
from pywebpush import webpush, WebPushException
from .models import Task, WebPushSubscription
from .utils.google_calendar import calendar_debug
from django.conf import settings

def send_webpush(user, title: str, body: str):
    calendar_debug(f"🚀 Sending push to, {user.email}")
    subs = WebPushSubscription.objects.filter(user=user)
    if not subs.exists():
        calendar_debug(f"🟡 No WebPushSubscription for {user.email}")
        return

    for sub in subs:
        try:
            res = webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": {"p256dh": sub.p256dh, "auth": sub.auth},
                },
                data=json.dumps({"title": title, "body": body}),
                vapid_private_key=settings.WEBPUSH_SETTINGS["VAPID_PRIVATE_KEY"],
                vapid_claims={"sub": "mailto:admin@taskmentor.ru"},
            )
            calendar_debug(f"✅ WebPush sent to {user.email}: {getattr(res, 'status_code', 'ok')}")
        except WebPushException as e:
            # самое полезное — статус/ответ от push сервиса
            print(f"❌ WebPushException for {user.email}: {e}")
            if getattr(e, "response", None) is not None:
                print("   status:", e.response.status_code)
                try:
                    print("   body:", e.response.text)
                except Exception:
                    pass
        except Exception as e:
            print(f"❌ WebPush error for {user.email}: {e}")

def reminder_tick():
    """
    Каждую минуту:
    - берём невыполненные задачи, у которых дедлайн в ближайшие 30 минут
    - шлём push ученику
    (и при желании учителю тоже)
    """
    now = timezone.now()
    now_local = timezone.localtime(now)
    window_end = now + timezone.timedelta(minutes=60)

    qs = (
        Task.objects
        .select_related("student", "teacher")
        .filter(
            is_completed=False,
            due_date__gte=now,
            due_date__lte=window_end,
            last_reminded_at__isnull=True
        )
    )
    calendar_debug(f"⏱ APScheduler tick, {timezone.now()}")

    for task in qs:
        title = "⏰ Скоро дедлайн"
        body = f"{task.title} — до {task.due_date.astimezone(timezone.get_current_timezone()).strftime('%d.%m %H:%M')}"

        # отправляем (если подписок нет — просто ничего не произойдет)
        send_webpush(task.student, title, body)
        send_webpush(task.teacher, title, body)

        # отмечаем, что напоминание уже было
        Task.objects.filter(id=task.id, last_reminded_at__isnull=True).update(last_reminded_at=now)

def start_scheduler():
    calendar_debug("✅ APScheduler: init scheduler object")
    scheduler = BackgroundScheduler(timezone=str(timezone.get_current_timezone()))
    scheduler.add_job(reminder_tick, "interval", minutes=2, id="task_reminders", replace_existing=True)
    scheduler.start()
    calendar_debug("✅ APScheduler: job added + scheduler.start() called")
    return scheduler

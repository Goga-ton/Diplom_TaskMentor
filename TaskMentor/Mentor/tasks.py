import json
from datetime import timedelta

from celery import shared_task
from django.utils import timezone
from django.conf import settings
from pywebpush import webpush

from .models import Task


@shared_task
def send_due_soon_push_reminders(minutes_ahead: int = 30):
    """
    Каждую минуту:
    - находим невыполненные задачи с due_date в ближайшие minutes_ahead минут
    - если reminded_at пустой -> отправляем push ученику
    - ставим reminded_at, чтобы не отправлять повторно
    """
    now = timezone.now()
    window_end = now + timedelta(minutes=minutes_ahead)

    qs = (
        Task.objects
        .filter(is_completed=False, reminded_at__isnull=True)
        .filter(due_date__gte=now, due_date__lte=window_end)
        .select_related("student")
    )

    for task in qs:
        student = task.student
        subs = student.push_subscriptions.all()

        # Если подписок нет — молча помечаем как обработанную
        if not subs.exists():
            task.reminded_at = timezone.now()
            task.save(update_fields=["reminded_at"])
            continue

        payload = json.dumps({
            "title": "⏰ Скоро дедлайн",
            "body": f"{task.title} — до {timezone.localtime(task.due_date).strftime('%d.%m.%Y %H:%M')}"
        })

        for sub in subs:
            try:
                webpush(
                    subscription_info={
                        "endpoint": sub.endpoint,
                        "keys": {"p256dh": sub.p256dh, "auth": sub.auth}
                    },
                    data=payload,
                    vapid_private_key=settings.WEBPUSH_SETTINGS["VAPID_PRIVATE_KEY"],
                    vapid_claims={"sub": settings.WEBPUSH_SETTINGS["VAPID_ADMIN_EMAIL"]},
                )
            except Exception:
                # позже можно будет чистить битые подписки, пока просто пропускаем
                pass

        task.reminded_at = timezone.now()
        task.save(update_fields=["reminded_at"])

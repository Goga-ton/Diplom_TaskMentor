import os
import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings

_app = None

def _get_app():
    """
    Инициализация Firebase Admin singleton.
    """
    global _app
    if _app is not None:
        return _app

    if not getattr(settings, "FCM_ENABLED", False):
        return None

    path = getattr(settings, "FIREBASE_SERVICE_ACCOUNT_PATH", "") or ""
    if not path or not os.path.exists(path):
        # В дипломе это нормально: интеграция есть, но ключи не настроены.
        return None

    cred = credentials.Certificate(path)
    _app = firebase_admin.initialize_app(cred)
    return _app


def send_fcm_to_token(token: str, title: str, body: str, data: dict | None = None, dry_run: bool = False):
    """
    Отправка пуша на конкретный device token.
    dry_run=True позволяет проверить серверную часть (запрос в FCM) без доставки.
    """
    app = _get_app()
    if app is None:
        return {"ok": False, "error": "FCM is disabled or not configured"}

    msg = messaging.Message(
        token=token,
        notification=messaging.Notification(title=title, body=body),
        data={k: str(v) for k, v in (data or {}).items()},
    )

    try:
        message_id = messaging.send(msg, dry_run=dry_run)
        return {"ok": True, "message_id": message_id, "dry_run": dry_run}
    except Exception as e:
        # Важно: это как раз то, что мы сможем проверять без мобилки
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}

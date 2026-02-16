from django.conf import settings

def webpush_settings(request):
    return {
        "WEBPUSH_SETTINGS": getattr(settings, "WEBPUSH_SETTINGS", {}),
    }

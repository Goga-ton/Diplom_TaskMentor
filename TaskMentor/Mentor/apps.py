# from django.apps import AppConfig
#
#
# class MentorConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'Mentor'
#
#     def ready(self):
#         try:
#             import Mentor.signals
#             print("🔥 Mentor.signals LOADED!")  # тест
#         except ImportError as e:
#             print(f"❌ Signals error: {e}")

from django.apps import AppConfig
import os

class MentorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Mentor'

    def ready(self):
        # APScheduler запускать только в основном процессе runserver
        if os.environ.get("RUN_MAIN") == "true":
            print("✅ APScheduler: starting...")
            from .scheduler import start_scheduler
            start_scheduler()
            print("✅ APScheduler: started")
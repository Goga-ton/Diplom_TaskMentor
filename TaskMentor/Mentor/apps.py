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
from django.apps import AppConfig


class MentorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Mentor'

    def ready(self):
        # import Mentor.signals
        pass

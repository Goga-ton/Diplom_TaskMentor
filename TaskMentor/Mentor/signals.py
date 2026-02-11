# from django.dispatch import receiver
# from allauth.socialaccount.signals import pre_social_login, social_account_added
# from .models import GoogleCalendarToken
# from django.utils import timezone
# from datetime import timedelta
#
# @receiver(social_account_added)
# def save_real_google_token(sender, request, sociallogin=None, **kwargs):
#     """
#       Сохраняем OAuth-токены Google в GoogleCalendarToken
#       после успешного подключения Google-аккаунта.
#     """
#     if sociallogin is None or sociallogin.account.provider.lower() != "google":
#         return
#
#     user = sociallogin.user
#     # if getattr(user, "user_type", None) != "teacher":
#     if getattr(user, "user_type", None) not in ("teacher", "student"):
#         return
#
#     # Токен обычно лежит в sociallogin.token (а refresh — в token_secret)
#     token = getattr(sociallogin, "token", None)
#     if not token or not getattr(token, "token", None):
#         return
#
#     access_token = token.token
#     refresh_token = getattr(token, "token_secret", "") or ""
#
#     GoogleCalendarToken.objects.update_or_create(
#         user=user,
#         defaults={
#             "access_token": access_token,
#             "refresh_token": refresh_token,
#             "token_expiry": timezone.now() + timedelta(hours=1),
#             "calendar_id": "primary",
#         },
#     )
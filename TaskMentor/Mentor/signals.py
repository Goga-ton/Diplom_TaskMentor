from django.dispatch import receiver
from allauth.socialaccount.signals import pre_social_login, social_account_added
from .models import GoogleCalendarToken
from django.utils import timezone
from datetime import timedelta


# @receiver(pre_social_login)
# def save_token_on_login(sender, request, sociallogin, **kwargs):
#     if sociallogin.account.provider == 'google':
#         print(f"🔍 SAVE_TOKEN: Google login detected")
#
#         if hasattr(sociallogin, 'token') and hasattr(sociallogin.token, 'token'):
#             token_value = sociallogin.token.token
#             refresh_value = getattr(sociallogin.token, 'refresh_token', '')
#             print(
#                 f"🔍 SAVE_TOKEN: Token: {token_value[:30]}..., Refresh: {refresh_value[:30] if refresh_value else 'None'}...")
#
#             # Сохраняем в сессию
#             request.session['google_calendar_token'] = token_value
#             request.session['google_refresh_token'] = refresh_value
#             request.session['google_token_saved'] = True
#             print(f"🔍 SAVE_TOKEN: Tokens saved to session")

@receiver(social_account_added)
def save_real_google_token(sender, request, sociallogin=None, **kwargs):
    """
      Сохраняем OAuth-токены Google в GoogleCalendarToken
      после успешного подключения Google-аккаунта.
    """
    if sociallogin is None or sociallogin.account.provider.lower() != "google":
        return

    user = sociallogin.user
    if getattr(user, "user_type", None) != "teacher":
        return

    # Токен обычно лежит в sociallogin.token (а refresh — в token_secret)
    token = getattr(sociallogin, "token", None)
    if not token or not getattr(token, "token", None):
        return

    access_token = token.token
    refresh_token = getattr(token, "token_secret", "") or ""

    GoogleCalendarToken.objects.update_or_create(
        user=user,
        defaults={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_expiry": timezone.now() + timedelta(hours=1),
            "calendar_id": "primary",
        },
    )

# # Получаем actual signal объекты
# from allauth.socialaccount.signals import pre_social_login, social_account_added
#
# # Проверяем сколько receivers зарегистрировано
# pre_receivers = len(pre_social_login.receivers) if hasattr(pre_social_login, 'receivers') else 0
# add_receivers = len(social_account_added.receivers) if hasattr(social_account_added, 'receivers') else 0
#
# print(f"🔥 DEBUG: pre_social_login receivers count: {pre_receivers}")
# print(f"🔥 DEBUG: social_account_added receivers count: {add_receivers}")
#
# # Выводим сами receivers (первые 3)
# if hasattr(pre_social_login, 'receivers'):
#     for i, receiver in enumerate(pre_social_login.receivers[:3]):
#         print(f"🔥 DEBUG: pre_social_login receiver {i}: {receiver}")
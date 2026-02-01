from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.socialaccount.signals import pre_social_login
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from .models import User, GoogleCalendarToken
from datetime import datetime, timedelta, timezone
from allauth.socialaccount.signals import social_account_added


@receiver(pre_social_login)
def link_google_account(sender, request, sociallogin, **kwargs):
    email = sociallogin.account.extra_data['email']
    try:
        user = User.objects.get(email=email)
        # Логиним существующего пользователя
        sociallogin.connect(request, user)
        login(request, user)
        # Редирект по роли
        if user.user_type == 'teacher':
            return HttpResponseRedirect('/teacher/dashboard/')
        else:
            return HttpResponseRedirect('/student/dashboard/')
    except User.objects.ModelMultipleResults:
        # Несколько пользователей с email — ошибка
        sociallogin.state['process'] = 'connect'
    except User.DoesNotExist:
        # Нет аккаунта — редирект на регистрацию
        pass


@receiver(social_account_added)
def save_google_token(sender, socialaccount, **kwargs):
    user = socialaccount.user
    print(f"🚨 ADDED: provider={socialaccount.provider}, user={user.email}")

    if (socialaccount.provider == 'google' and
            user.usertype == 'teacher'):

        # Token из socialaccount
        token = socialaccount.tokens.first()
        if token:
            print(f"🚨 TOKEN: {token.token[:20]}")
            GoogleCalendarToken.objects.update_or_create(
                user=user,
                defaults={
                    'access_token': token.token,
                    'refresh_token': getattr(token, 'refresh_token', token.token),
                    'token_expiry': timezone.now() + timedelta(hours=1),
                }
            )
            print("🚨 TOKEN SAVED!")
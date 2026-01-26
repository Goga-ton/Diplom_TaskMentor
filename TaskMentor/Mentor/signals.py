from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.socialaccount.signals import pre_social_login
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from .models import User

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
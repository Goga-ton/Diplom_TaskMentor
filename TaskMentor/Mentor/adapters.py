from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from allauth.account.utils import perform_login
from allauth.account.adapter import DefaultAccountAdapter

from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.shortcuts import redirect
from django.utils import timezone
from datetime import timedelta

from .models import GoogleCalendarToken


User = get_user_model()


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    1) Запрещаем auto-signup через Google (вход только для уже зарегистрированных).
    2) Если email существует — подключаем (connect) social account к существующему User.
    3) Сохраняем access/refresh токены в GoogleCalendarToken (как у тебя было).
    """

    def pre_social_login(self, request, sociallogin):
        print("🔥 ADAPTER pre_social_login CALLED")
        print("🔥 provider =", sociallogin.account.provider)
        print("🔥 email =", (sociallogin.user.email or "").strip().lower())

        # ✅ если пользователь уже залогинен и нажал "подключить" — не вмешиваемся
        if request.user.is_authenticated:
            return

        """
        Вызывается ДО завершения social login.
        Если пользователь ещё не существует в системе allauth, пытаемся найти
        пользователя по email и "подключить" к нему Google-аккаунт.
        """
        provider = (sociallogin.account.provider or "").lower()
        if provider != "google":
            return

        # email может лежать в разных местах, берём максимально надёжно
        email = (sociallogin.user.email or "").strip().lower()
        if not email:
            email = (sociallogin.account.extra_data.get("email") or "").strip().lower()

        if not email:
            messages.error(request, "Google не передал email. Вход невозможен.")
            # raise ImmediateHttpResponse(redirect("index"))
            return

        # Если sociallogin уже связан с existing user — ничего не делаем
        if sociallogin.is_existing:
            return

        # Ищем пользователя в нашей базе
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Этот email не зарегистрирован в TaskMentor. Сначала зарегистрируйтесь.")
            # raise ImmediateHttpResponse(redirect("index"))
            return

        # Разрешаем Google-вход для учителя и ученика (по твоей новой логике)
        if getattr(user, "user_type", None) not in ("teacher", "student"):
            messages.error(request, "Этот аккаунт не поддерживает вход через Google.")
            # raise ImmediateHttpResponse(redirect("index"))
            return

        # Подключаем Google social account к существующему пользователю
        sociallogin.connect(request, user)

    def is_open_for_signup(self, request, sociallogin):
        """
        Гарантированно запрещаем создание новых пользователей через соцлогин.
        """
        return False

    def save_token(self, request, sociallogin, token):
        print("🔥 ADAPTER save_token CALLED")
        print("🔥 provider =", sociallogin.account.provider)
        print("🔥 access_token =", (token.token or "")[:20])
        print("🔥 refresh_token =", (token.token_secret or "")[:20])
        """
        Оставляем твою логику сохранения токена в GoogleCalendarToken.
        """
        super().save_token(request, sociallogin, token)

        provider = (sociallogin.account.provider or "").lower()
        if provider != "google":
            return

        user = sociallogin.user

        access_token = token.token
        # В allauth refresh_token часто хранится в token_secret
        refresh_token = token.token_secret or ""

        if access_token and access_token != "dummy_access_token":
            GoogleCalendarToken.objects.update_or_create(
                user=user,
                defaults={
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_expiry": timezone.now() + timedelta(hours=1),
                    "calendar_id": "primary",
                },
            )

class CustomAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        user = request.user
        if getattr(user, "user_type", None) == "teacher":
            return "/teacher/dashboard/"
        if getattr(user, "user_type", None) == "student":
            return "/student/dashboard/"
        return "/"
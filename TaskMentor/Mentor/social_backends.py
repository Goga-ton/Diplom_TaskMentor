# from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
# from .models import GoogleCalendarToken
# from django.utils import timezone
# from datetime import timedelta
#
#
# class GoogleBackend(GoogleOAuth2Adapter):
#     def complete_login(self, request, app, token, **kwargs):
#         print("🚀 GOOGLE BACKEND!")
#
#         user = getattr(request, 'user', None)
#         if user and user.user_type == 'teacher':
#             GoogleCalendarToken.objects.update_or_create(
#                 user=user,
#                 defaults={
#                     'access_token': token['access_token'],
#                     'refresh_token': token.get('refresh_token', ''),
#                     'token_expiry': timezone.now() + timedelta(hours=1),
#                 }
#             )
#             print("🚀 TOKEN SAVED!")
#
#         return super().complete_login(request, app, token, **kwargs)

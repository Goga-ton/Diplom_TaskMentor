from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (User, TeacherProfile, StudentProfile,
                     WebPushSubscription, GoogleCalendarToken, Task,
                     FCMDeviceToken)

class TeacherProfileInline(admin.StackedInline):
    model = TeacherProfile
    can_delete = False

class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    fk_name = 'user'  # ← КРИТИЧНО!
    can_delete = False

@admin.register(User)
class UserAdmin(UserAdmin):
    inlines = [TeacherProfileInline, StudentProfileInline]
    ordering = ['email']  # ✅ Принудительно после удаления из list_display('username',) без этой строки не шла миграция
    list_display = ['email', 'first_name', 'user_type'] # удалил ('username',) не позволял сделать миграцию для обнуления 'username'
    list_filter = ['user_type']
    search_fields = ['email', 'first_name']

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    pass

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'nickname', 'teacher']
    list_filter = ['teacher']

@admin.register(WebPushSubscription)
class WebPushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'endpoint', 'created_at']
    list_filter = ['created_at']

@admin.register(GoogleCalendarToken)
class GoogleCalendarTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'calendar_id', 'token_expiry']
    list_filter = ['token_expiry']
    search_fields = ['user__email']
    readonly_fields = ['access_token', 'refresh_token', 'token_expiry', 'calendar_id']  # Токены только для чтения

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "teacher", "student", "due_date", "is_completed", "reminded_at", "last_reminded_at")
    list_filter = ("is_completed", "priority")
    search_fields = ("title", "student__email", "teacher__email")
    readonly_fields = ("teacher_calendar_event_id", "student_calendar_event_id")

@admin.register(FCMDeviceToken)
class FCMDeviceTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "platform", "is_active", "created_at", "last_seen_at")
    list_filter = ("platform", "is_active")
    search_fields = ("user__email", "token")
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, TeacherProfile, StudentProfile, WebPushSubscription

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
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, TeacherProfile, StudentProfile

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
    list_display = ['email', 'username', 'first_name', 'user_type']
    list_filter = ['user_type']
    search_fields = ['email', 'first_name']

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    pass

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'nickname', 'teacher']
    list_filter = ['teacher']
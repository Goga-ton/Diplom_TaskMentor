from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib.auth import get_user_model

from .models import StudentApplication
from .forms import (
    TeacherRegistrationForm,
    StudentApplicationForm,
    EmailAuthenticationForm,
    # StudentRegistrationForm,
)

User = get_user_model()

@csrf_protect
def index(request):
    return render(request, 'core/index.html')

@csrf_protect
def teacher_register(request):
    if request.method == 'POST': # так и не понял что проверяет эта строка
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend' #данная строка опредеяет кто разрешает вход для строки ниже
            login(request, user) #данная строка производит автоматический код с разрешения полученного в предыдущей строке
            return redirect('teacher_dashboard')
    else:
        form = TeacherRegistrationForm()
    return render(request, 'core/auth/register.html', {
        'form': form,
        'role': 'teacher',
        'title': 'Регистрация наставника',
    })


def student_application(request):
    if request.method == 'POST':
        form = StudentApplicationForm(request.POST)
        if form.is_valid():
            StudentApplication.objects.create(
                teacher=User.objects.get(email=form.cleaned_data['teacher_email']),
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['first_name'],
                phone=form.cleaned_data['phone'],
                telegram=form.cleaned_data.get('telegram', ''),
                nickname=form.cleaned_data['nickname']
            )
            return render(request, 'core/auth/student_application.html', {
                'form': form,
                'title': 'Заявка отправлена! Учитель получит уведомление.',
                'message': 'Спасибо! Данные отправлены учителю.'
            })
    else:
        form = StudentApplicationForm()

    return render(request, 'core/auth/student_application.html', {
        'form': form,
        'title': 'Отправить заявку на регистрацию'
    })

# Блок регистрации ученика
# @csrf_protect
# def student_register(request):
#     if request.method == 'POST':
#         form = StudentRegistrationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             user.backend = 'django.contrib.auth.backends.ModelBackend'
#             login(request, user)
#             login(request, user)
#             return redirect('student_dashboard')
#     else:
#         form = StudentRegistrationForm()
#     return render(request, 'core/auth/register.html', {
#         'form': form,
#         'role': 'student',
#         'title': 'Регистрация ученика',
#     })

@csrf_protect
def user_login(request):
    role = request.POST.get('role', request.GET.get('role', ''))
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if role and user.user_type != role:
                messages.error(request, 'Неверная роль для этого аккаунта')
            else:
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
                if user.user_type == 'teacher':
                    return redirect('teacher_dashboard')
                else:
                    return redirect('student_dashboard')
    else:
        form = EmailAuthenticationForm(request)
    return render(request, 'core/auth/login.html', {
        'form': form,
        'role': role,
    })


@login_required
def user_logout(request):
    logout(request)
    return redirect('index')

@login_required
def teacher_dashboard(request):
    if request.user.user_type != 'teacher':  # Проверка роли
        return redirect('index')

    applications = StudentApplication.objects.filter(
        teacher=request.user,
        status='pending'
    ).order_by('-created_at')

    return render(request, 'core/teacher_dashboard.html', {
        'applications': applications
    })

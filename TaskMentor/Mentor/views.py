from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth import get_user_model
import json
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password

from .models import StudentApplication, StudentProfile
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
                messages.error(request, f'Вы зарегистрированы как {user.user_type}, выберите соответствующую роль.')
                form = EmailAuthenticationForm(request)
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

@require_http_methods(["POST"])
@csrf_protect
def ajax_login(request):
    role = request.POST.get('role')
    email = request.POST.get('email')
    password = request.POST.get('password')

    user = authenticate(request, email=email, password=password)
    if user:
        if role and user.user_type != role:
            return JsonResponse({
                'success': False,
                'message': f'Вы {user.user_type}. Выберите соответствующую роль.'
            })

        login(request, user)
        return JsonResponse({
            'success': True,
            'redirect': reverse('teacher_dashboard') if user.user_type == 'teacher' else reverse('student_dashboard')
        })

    return JsonResponse({
        'success': False,
        'message': 'Неверный email или пароль'
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


@login_required
def toggle_application_status(request, app_id, action):
    action in ['approve', 'reject']
    if request.user.usertype != 'teacher':
        return JsonResponse({'success': False, 'message': 'Только для учителей'})

    app = get_object_or_404(StudentApplication, id=app_id, teacher=request.user)

    if action == 'approve':
        app.status = 'approved'
        message = 'Заявка одобрена'
    elif action == 'reject':
        app.status = 'rejected'
        message = 'Заявка отклонена'
    else:
        return JsonResponse({'success': False, 'message': 'Неверное действие'})

    app.save()
    return JsonResponse({'success': True, 'message': message})
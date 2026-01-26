from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from .forms import (
    TeacherRegistrationForm,
    StudentRegistrationForm,
    EmailAuthenticationForm,
)

@csrf_protect
def index(request):
    return render(request, 'core/index.html')

@csrf_protect
def teacher_register(request):
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            return redirect('teacher_dashboard')
    else:
        form = TeacherRegistrationForm()
    return render(request, 'core/auth/register.html', {
        'form': form,
        'role': 'teacher',
        'title': 'Регистрация наставника',
    })


@csrf_protect
def student_register(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            login(request, user)
            return redirect('student_dashboard')
    else:
        form = StudentRegistrationForm()
    return render(request, 'core/auth/register.html', {
        'form': form,
        'role': 'student',
        'title': 'Регистрация ученика',
    })

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
    if request.user.user_type != 'teacher':
        return HttpResponseForbidden("Доступ только учителям")
    return render(request, 'core/teacher_dashboard.html')

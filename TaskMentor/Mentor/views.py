from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse


@csrf_protect
def index(request):
    return render(request, 'core/index.html')


@csrf_protect
def user_login(request):
    role = request.POST.get('role', request.GET.get('role', ''))
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)
        if user:
            if user.user_type == role:
                login(request, user)
                if role == 'teacher':
                    return redirect('teacher_dashboard')
                else:
                    return redirect('student_dashboard')
            else:
                messages.error(request, 'Неверная роль для этого аккаунта')
        else:
            messages.error(request, 'Неверный email или пароль')

    return render(request, 'core/index.html')


def register(request):
    role = request.GET.get('role')
    # Пока редирект на форму регистрации (создадим позже)
    return render(request, 'core/auth/register.html', {'role': role})


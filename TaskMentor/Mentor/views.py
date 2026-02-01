from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
import json
from django.views.decorators.http import require_http_methods, require_POST
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.db.models import Case, When, Value, IntegerField, FloatField, ExpressionWrapper, Count, Q
from django.db.models.functions import TruncDay
from datetime import timedelta, date
from django.conf import settings
import math
from collections import defaultdict
from pywebpush import webpush, WebPushException

from .models import StudentApplication, StudentProfile, User, Task, MoodEntry, WebPushSubscription
from .forms import (
    TeacherRegistrationForm,
    StudentApplicationForm,
    EmailAuthenticationForm,
    MoodEntryForm,
    # StudentRegistrationForm,
)


User = get_user_model()

@csrf_protect
def index(request):
    return render(request, 'core/index.html',{'WEBPUSH_SETTINGS': settings.WEBPUSH_SETTINGS})

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
    # ФИЛЬТР ЗАДАЧ (новое!)
    filter_status = request.GET.get('filter', 'pending')
    # students = StudentProfile.objects.filter(teacher=request.user)
    # Базовый queryset всех задач учителя
    all_tasks = Task.objects.filter(teacher=request.user)

    if filter_status == 'pending':
        tasks = all_tasks.filter(is_completed=False)  # Только не выполненные (по умолчанию)
    else:  # 'all'
        tasks = all_tasks  # Все задачи

    applications = StudentApplication.objects.filter(
        teacher=request.user,
        status='pending' #показывает заявки только с этим статусом
    ).order_by('-created_at')
    student_profiles = StudentProfile.objects.filter(teacher=request.user).select_related('user')
    # students = StudentProfile.objects.filter(teacher=request.user) # старая строка взамен той которая выше

    # === АНАЛИТИКА УЧИТЕЛЯ ===
    # students_with_stats = []
    # for student_profile in students:
    #     student = student_profile.user
    students_with_stats = []
    for profile in student_profiles:
        student = profile.user

        # Прогресс задач
        total_tasks = Task.objects.filter(student=student).count()
        completed_tasks = Task.objects.filter(student=student, is_completed=True).count()
        progress = round((completed_tasks / total_tasks) * 100) if total_tasks else 0

        # Настроение за 7 дней
        recent_moods = MoodEntry.objects.filter(
            student=student, date__gte=timezone.now().date() - timedelta(days=7)
        ).order_by("-date")[:7]

        # Получаем задачи студента для отображения
        student_tasks = all_tasks.filter(student=student)
        if filter_status == 'pending':
            student_tasks = student_tasks.filter(is_completed=False)


        students_with_stats.append({
            "user": student,  # Основной пользователь
            "profile": profile,  # StudentProfile
            "progress": progress,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "recent_moods": recent_moods,
            "tasks": student_tasks,  # Задачи студента с учетом фильтра
            # "profile": student_profile,
            # "progress": progress,
            # "total_tasks": total_tasks,
            # "completed_tasks": completed_tasks,
            # "recent_moods": recent_moods,
        })

    return render(request, 'core/teacher_dashboard.html', {
        'applications': applications,
        'students': students_with_stats,
        'tasks': tasks,  # Передаём отфильтрованные задачи
        'filter_status': filter_status,  # Для шаблона
        'now': timezone.now()
    })


@login_required
def student_dashboard(request):
    if request.user.user_type != 'student':
        return redirect('index')

    view_mode = request.GET.get('view', 'recommended')

    profile = request.user.student_profile  # Связь из модели
    now = timezone.now()

    priority_weight_expr = Case(
        When(priority='high', then=Value(3)),
        When(priority='medium', then=Value(2)),
        When(priority='low', then=Value(1)),
        default=Value(0),
        output_field=IntegerField(),
    )

    base_qs = (
        Task.objects
        .filter(student=request.user, is_completed=False)
        .annotate(priority_weight=priority_weight_expr)
    )

    # 2.4 + 2.4.1: Overdue — отдельной группой, high->medium->low, внутри — по самой большой просрочке
    overdue_qs = base_qs.filter(due_date__lt=now).order_by('-priority_weight', 'due_date')

    # Остальные (пока просто по дате, дальше заменим на срочность из 2.1)
    upcoming_qs = base_qs.filter(due_date__gte=now).order_by('due_date')

    if view_mode == '24hours':
        end = now + timedelta(hours=24)
        tasks = list(upcoming_qs.filter(due_date__lte=end).order_by('due_date'))
        return render(request, 'core/student_dashboard.html', {
            'profile': profile,
            'teacher': profile.teacher,
            'tasks': tasks,
            'now': now,
            'view_mode': view_mode,
        })

    upcoming_tasks = list(upcoming_qs)

    for t in upcoming_tasks:
        delta_seconds = (t.due_date - now).total_seconds()
        days_left = delta_seconds / 86400
        days_left_ceil = max(0, math.ceil(days_left))  # на всякий случай
        t.days_left_ceil = days_left_ceil
        t.urgency = t.priority_weight / (days_left_ceil + 1)

    # upcoming_tasks.sort(key=lambda t: t.urgency, reverse=True)
    if view_mode == 'date':
        # Просроченные всё равно сверху, но внутри upcoming — по due_date (ближайшие сначала)
        upcoming_tasks.sort(key=lambda t: t.due_date)
    elif view_mode == 'priority':
        upcoming_tasks.sort(key=lambda t: (-t.priority_weight, t.due_date))
        # tasks = list(overdue_qs) + upcoming_tasks
    # elif view_mode == 'hot': # ХЗ вообще зачем нужен
    #     upcoming_tasks.sort(key=lambda t: (-t.urgency, -t.priority_weight, t.due_date))
    else:
        # recommended (как сейчас)
        upcoming_tasks.sort(key=lambda t: t.urgency, reverse=True)

    tasks = list(overdue_qs) + upcoming_tasks

    # tasks = list(overdue_qs) + upcoming_tasks
    # tasks = Task.objects.filter(student=request.user).order_by('due_date') #старый код

    # --- Этап 3: самочувствие сегодня ---
    today = timezone.localdate()

    mood_entry, _ = MoodEntry.objects.get_or_create(
        student=request.user,
        date=today,
        defaults={"mood": "good"},
    )

    if request.method == "POST" and request.POST.get("form") == "mood":
        mood_form = MoodEntryForm(request.POST, instance=mood_entry)
        if mood_form.is_valid():
            mood_form.save()
            return redirect("student_dashboard")
    else:
        mood_form = MoodEntryForm(instance=mood_entry)

    # --- Этап 3: прогресс (процент выполненных задач) ---
    total_tasks = Task.objects.filter(student=request.user).count()
    completed_tasks = Task.objects.filter(student=request.user, is_completed=True).count()
    progress_percent = round((completed_tasks / total_tasks) * 100) if total_tasks else 0

    # --- Графики: настроение за 30 дней ---
    moods_30days = MoodEntry.objects.filter(
        student=request.user,
        date__gte=timezone.now().date() - timedelta(days=30)
    ).values("date").annotate(count=Count("mood")).order_by("date")

    # Преобразуем в словарь {дата: mood_value}
    mood_data = {}
    for entry in MoodEntry.objects.filter(student=request.user, date__gte=timezone.now().date() - timedelta(days=30)):
        mood_map = {"great": 3, "good": 2, "bad": 1}
        mood_data[entry.date.strftime("%Y-%m-%d")] = mood_map[entry.mood]

    # --- Графики: задачи по дням за 30 дней ---
    tasks_by_day = Task.objects.filter(
        student=request.user,
        created_at__gte=timezone.now() - timedelta(days=30)
    ).annotate(day=TruncDay("created_at")).values("day").annotate(
        created=Count("id", filter=Q(is_completed=False)),
        completed=Count("id", filter=Q(is_completed=True))
    )

    task_data = {}
    for item in tasks_by_day:
        day_str = item["day"].strftime("%Y-%m-%d")
        task_data[day_str] = {
            "created": item["created"],
            "completed": item["completed"]
        }

    return render(request, 'core/student_dashboard.html', {
        'profile': profile,
        'teacher': profile.teacher,
        'tasks': tasks,  # ➕ Передача задач
        'now': now,
        'view_mode': view_mode,
        "mood_form": mood_form,
        "mood_entry": mood_entry,
        "progress_percent": progress_percent,
        "completed_tasks": completed_tasks,
        "total_tasks": total_tasks,
        "mood_data": mood_data,
        "task_data": task_data,
    })

@login_required
def toggle_application_status(request, app_id, action):
    if action not in ['approve', 'reject']:
        return JsonResponse({'success': False, 'message': 'Неверное действие'})

    if request.user.user_type != 'teacher':
        return JsonResponse({'success': False, 'message': 'Только для учителей'})

    app = get_object_or_404(StudentApplication, id=app_id, teacher=request.user)

    if action == 'approve':
        student_password = request.META.get('HTTP_X_STUDENT_PASSWORD')
        if not student_password:
            return JsonResponse({'success': False, 'message': 'Пароль не передан'})

        # Проверяем, нет ли уже ученика с таким email
        if User.objects.filter(email=app.email).exists():
            return JsonResponse({'success': False, 'message': 'Ученик уже существует'})

        # ✅ Фикс telegram UNIQUE (временное решение чтобы не делать миграцию, как будет делать минрацию ремим строку ниже возвращаем (telegram=app.telegram or '',) в student
        # telegram_candidate = app.telegram.strip() if app.telegram and app.telegram.strip() else ''
        # if telegram_candidate and User.objects.filter(telegram=telegram_candidate).exists():
        #     telegram_candidate = ''  # fallback на пустую строку

        # Создаём User (студент)
        student = User.objects.create_user(
            # username=f"user_{app_id}",
            email=app.email,
            first_name=app.first_name,
            phone=app.phone or '',
            telegram=app.telegram or '', #telegram=telegram_candidate,
            user_type='student',
            password=student_password  # Хешируется автоматически
        )

        # Создаём StudentProfile
        StudentProfile.objects.create(
            user=student,
            nickname=app.nickname,
            teacher=app.teacher
        )

        # Обновляем заявку
        app.teacher_set_password = student_password  # Сохраняем в заявке
        app.status = 'approved'
        app.save()
        message = f'Ученик {app.nickname} создан'
    elif action == 'reject':
        app.status = 'rejected'
        message = 'Заявка отклонена'
    else:
        return JsonResponse({'success': False, 'message': 'Неверное действие'})

    # app.save()
    return JsonResponse({'success': True, 'message': message})

@login_required
def create_task(request):
    if request.user.user_type != 'teacher':
        return HttpResponseForbidden()
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        if not student_id:
            messages.error(request, 'Укажите ученика')
            return redirect('teacher_dashboard')

        student = get_object_or_404(User, id=student_id, user_type='student')
        Task.objects.create(
            title=request.POST['title'],
            description=request.POST.get('description', ''),
            student=student,
            teacher=request.user,
            due_date=request.POST['due_date'],
            priority=request.POST['priority'],
            is_completed=False
        )
        messages.success(request, f'Задача "{request.POST["title"]}" создана для {student.first_name}!')
    return redirect('teacher_dashboard')

@login_required
def edit_task(request):
    if request.user.user_type != 'teacher':
        return HttpResponseForbidden()

    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        task = get_object_or_404(Task, id=task_id, teacher=request.user)

        task.title = request.POST['title']
        task.description = request.POST.get('description', '')
        task.due_date = request.POST['due_date']
        task.priority = request.POST['priority']
        # task.is_completed = request.POST.get('is_completed') == 'on' # это убирарает галочку Выполнено для учителя
        task.save()

        messages.success(request, f'Задача "{task.title}" обновлена!')

    return redirect('teacher_dashboard')

@login_required
def get_task_data(request, task_id):
    if request.user.user_type != 'teacher':
        return JsonResponse({'error': 'Доступ запрещён'}, status=403)

    try:
        task = get_object_or_404(Task, id=task_id, teacher=request.user)
        return JsonResponse({
            'title': task.title,
            'description': task.description,
            'due_date': task.due_date.isoformat() if task.due_date else '',
            'priority': task.priority,
            'is_completed': task.is_completed
        })
    except Exception as e:
        return JsonResponse({'error': 'Задача не найдена'}, status=404)

@login_required
def complete_task(request, task_id):
    if request.user.user_type != 'student':
        return JsonResponse({'success': False, 'error': 'Только для учеников'}, status=403)

    task = get_object_or_404(Task, id=task_id, student=request.user)
    task.is_completed = True
    task.save()

    return JsonResponse({
        'success': True,
        'message': 'Задача выполнена!',
        'task_id': task_id
    })

# class TaskDeleteView(View):
#     @method_decorator(require_http_methods(["POST"]))
#     @method_decorator(login_required)
#     def post(self, request, task_id):
#         task = get_object_or_404(Task, id=task_id, teacher=request.user.teacherprofile)
#         if task.is_completed:
#             return JsonResponse({'error': 'Можно удалять только не выполненные задачи.'}, status=400)
#         task.delete()  # ЖЁСТКОЕ удаление
#         return JsonResponse({'success': True, 'message': 'Задача удалена.'})


class TaskDeleteView(LoginRequiredMixin, View):
    def post(self, request, task_id):
        if request.user.user_type != 'teacher':
            return JsonResponse({'error': 'Доступ запрещён'}, status=403)

        task = get_object_or_404(Task, id=task_id, teacher=request.user)
        if task.is_completed:
            return JsonResponse({'error': 'Можно удалять только не выполненные задачи.'}, status=400)

        task.delete()
        return JsonResponse({'success': True, 'message': 'Задача удалена.'})


@csrf_exempt
@require_POST
def subscribe_push(request):
    try:
        # Парсим JSON из тела запроса
        body = json.loads(request.body)
        endpoint = body['endpoint']
        keys = body['keys']

        print(f"Подписка: {endpoint[:50]}...")  # debug

        WebPushSubscription.objects.update_or_create(
            user=request.user,
            endpoint=endpoint,
            defaults={
                'p256dh': keys['p256dh'],
                'auth': keys['auth'],
            }
        )
        return JsonResponse({'status': 'ok'})

    except Exception as e:
        print(f"Subscribe error: {e}")  # debug
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_POST
def test_notification(request):
    for sub in request.user.push_subscriptions.all():
        try:
            webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": {"p256dh": sub.p256dh, "auth": sub.auth}
                },
                data=json.dumps({  # ← json.dumps!
                    "title": "🔔 TaskMentor",
                    "body": "Тест push!"
                }),
                vapid_private_key=settings.WEBPUSH_SETTINGS["VAPID_PRIVATE_KEY"],
                vapid_claims={"sub": settings.WEBPUSH_SETTINGS["VAPID_ADMIN_EMAIL"]}
            )
        except Exception as ex:
            print(f"Push error: {ex}")
    return JsonResponse({'status': 'sent'})

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def save_push_subscription(request):
    try:
        sub_data = json.loads(request.body)
        WebPushSubscription.objects.update_or_create(
            user=request.user,
            defaults={
                'endpoint': sub_data['endpoint'],
                'p256dh': sub_data['keys']['p256dh'],
                'auth': sub_data['keys']['auth']
            }
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
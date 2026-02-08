from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

USER_TYPE_CHOICES = [
    ('teacher', 'Учитель (Коуч/Психолог)'),
    ('student', 'Ученик (Клиент)'),
]
SPECIALIZATION_CHOICES = [
    ('coach', 'Коуч'),
    ('psychologist', 'Психолог'),
    ('fitness_trainer', 'Фитнес-тренер'),
]

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'teacher')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser должен быть staff')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser должен быть superuser')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Общие поля для всех пользователей"""
    username = None
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')
    first_name = models.CharField('Имя*', max_length=50)
    phone = models.CharField('Телефон', max_length=20, blank=True)
    email = models.EmailField('Email адрес*', unique=True)
    # telegram = models.SlugField('Telegram ID', unique=True, blank=True)
    # перед миграцией заремить строку выше и разремить ниже и внести корректировки во views там есть описание
    telegram = models.SlugField('Telegram ID', unique=False, blank=True, null=True)
    objects = UserManager()

    # Скрываем стандартные поля Django
    # username = None # - эта строка делает невидимым стандартное поле Django "username"
    USERNAME_FIELD = 'email' # но основной логин = email (не до конца понимаю нах. эта строка - разобраться если не забуду)
    REQUIRED_FIELDS = [] # - это строка добавляет поля в суперюзера, если все заработает снести эту строку

    def __str__(self):
        return f"{self.first_name} ({self.get_user_type_display()})"


class TeacherProfile(models.Model):
    """Профиль учителя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'teacher'}, related_name='teacher_profile')
    specialization = models.CharField('Специализация', max_length=20, choices=SPECIALIZATION_CHOICES)
    pro_nickname = models.CharField('Псевдоним коуча', max_length=50)
    work_phone = models.CharField('Рабочий телефон', max_length=20, blank=True)

    class Meta:
        verbose_name = 'Профиль учителя'
        verbose_name_plural = 'Профили учителей'


class StudentProfile(models.Model):
    """Профиль ученика"""
    user = models.OneToOneField(User, on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'student'}, related_name='student_profile')
    nickname = models.CharField('Погоняло', max_length=50)
    teacher = models.ForeignKey(User, on_delete=models.PROTECT,  # нельзя удалить учителя с учениками
        limit_choices_to={'user_type': 'teacher'}, related_name='students')

    def clean(self):
        # Проверяем, что у ученика есть профиль учителя
        if self.teacher.student_profile is None:
            raise ValidationError('Учитель должен иметь профиль')

    class Meta:
        verbose_name = 'Профиль ученика'
        verbose_name_plural = 'Профили учеников'
        unique_together = ['user', 'teacher']  # один учитель на ученика

class StudentApplication(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_applications')
    email = models.EmailField()
    first_name = models.CharField(max_length=30)
    phone = models.CharField(max_length=20)
    telegram = models.CharField(max_length=50, blank=True)
    nickname = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')  # pending-новая (по умолчанию), approved учитель зарегистрировал ученика., rejected — учитель отклонил.
    teacher_set_password = models.CharField(max_length=128, blank=True, null=True, help_text="Пароль, установленный учителем")


class Task(models.Model):
    PRIORITY_CHOICES = [('low', 'Низкий'), ('medium', 'Средний'), ('high', 'Высокий')]
    title = models.CharField('Название задачи', max_length=200)
    description = models.TextField(blank=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE,
                                limit_choices_to={'user_type': 'student'},
                                related_name='tasks')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE,
                                limit_choices_to={'user_type': 'teacher'})
    due_date = models.DateTimeField('Срок')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    calendar_event_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.title} -> {self.student.first_name}"

class MoodEntry(models.Model): #модель настроения
    MOOD_CHOICES = [
        ("great", "Отлично"),
        ("good", "Хорошо"),
        ("bad", "Плохо"),
    ]

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={"user_type": "student"},
        related_name="mood_entries",
    )
    date = models.DateField()  # локальная дата ученика/сервера
    mood = models.CharField(max_length=10, choices=MOOD_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "date")
        ordering = ("-date",)

    def __str__(self):
        return f"{self.student.email} {self.date} {self.mood}"

class WebPushSubscription(models.Model):
    """Подписка браузера на уведомления"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='push_subscriptions'
    )
    p256dh = models.TextField()  # Публичный ключ клиента
    auth = models.TextField()  # Auth токен клиента
    endpoint = models.URLField(max_length=500)  # URL браузера для push
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'endpoint')  # один браузер на пользователя

    def __str__(self):
        return f"{self.user.email} → {self.endpoint[:50]}..."

class GoogleCalendarToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'teacher'})
    access_token = models.CharField(max_length=500)
    refresh_token = models.CharField(max_length=500, blank=True)
    token_expiry = models.DateTimeField()
    calendar_id = models.CharField(max_length=200, default='primary')  # 'primary' или custom

    def refresh_access_token(self): # заглушка, d gthcgtrnbdt lолжен обновлять истёкший access_token с помощью refresh_token через Google OAuth API.
        # Логика refresh (ниже в utils)
        pass

    def is_expired(self): #проверяtт, не истёк ли токен (token_expiry).
        from django.utils import timezone
        return timezone.now() >= self.token_expiry

    def __str__(self):
        return f"Calendar tokens for {self.user.email}"

    # class Meta: # это код из урока стр.26 п 5.1
    #     verbose_name = 'Пользователь'
    #     verbose_name_plural = 'Пользователи'

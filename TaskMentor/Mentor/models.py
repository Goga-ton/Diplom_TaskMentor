from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('teacher', 'Учитель (Коуч/Психолог)'),
        ('student', 'Ученик (Клиент)'),
    ]

    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')
    first_name = models.CharField('Имя', max_length=50)
    last_name = models.CharField('Фамилия', max_length=50)
    phone = models.CharField('Телефон', max_length=20, blank=True) #blank=True - не обязательно заполнять
    email = models.EmailField('Email адрес', unique=True)
    telegram_id = models.SlugField('Telegram ID', unique=True)


    class Meta:
        # Указываем ИМЯ МОДЕЛИ в формате 'app_label.ModelName'
        db_table = 'mentor_user'  # Опционально: кастомное имя таблицы

    def __str__(self):
        return f"{self.first_name} ({self.get_user_type_display()})"

    # class Meta: # это код из урока стр.26 п 5.1
    #     verbose_name = 'Пользователь'
    #     verbose_name_plural = 'Пользователи'

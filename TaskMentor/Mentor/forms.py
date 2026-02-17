from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model

from .models import TeacherProfile, MoodEntry

User = get_user_model()


class BaseRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Пароль*',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='Повторите пароль*',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'phone', 'telegram']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'telegram': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует')
        return email

    def clean_telegram(self):
        telegram = self.cleaned_data.get('telegram', '').strip()
        if telegram and User.objects.filter(telegram=telegram).exists():
            raise forms.ValidationError('Этот Telegram ID уже используется')
        return telegram

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Пароли не совпадают')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email'].lower()
        user.set_password(self.cleaned_data['password1'])
        # user.username = user.email # username = email (уникальный)
        if commit:
            user.save()
        return user


class TeacherRegistrationForm(BaseRegistrationForm):
    specialization = forms.ChoiceField(
        label='Специализация*',
        choices=TeacherProfile._meta.get_field('specialization').choices,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    pro_nickname = forms.CharField(
        label='Псевдоним*',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    work_phone = forms.CharField(
        label='Рабочий телефон',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'teacher'
        if commit:
            user.save()
            TeacherProfile.objects.create(
                user=user,
                specialization=self.cleaned_data['specialization'],
                pro_nickname=self.cleaned_data['pro_nickname'],
                work_phone=self.cleaned_data['work_phone'],
            )
        return user


class StudentApplicationForm(forms.Form):
    first_name = forms.CharField(label='Имя', max_length=30, required=True)
    email = forms.EmailField(label='Ваш Email', max_length=254, required=True)
    nickname = forms.CharField(label='Никнейм', max_length=50, required=True)
    phone = forms.CharField(label='Телефон', max_length=20, required=False)
    telegram = forms.CharField(label='Telegram', max_length=50, required=False)
    teacher_email = forms.EmailField(label='Email Учителя (из системы)', required=True)

    def clean_teacher_email(self):
        teacher_email = self.cleaned_data['teacher_email']
        # Проверка: существует User с role='teacher' и этим email
        if not User.objects.filter(email=teacher_email, user_type='teacher').exists():
            raise forms.ValidationError('Указанный Email учителя не найден в системе!')
        return teacher_email


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'autofocus': True, 'class': 'form-control'})
    )
    password = forms.CharField(
        label='Пароль',
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )


class MoodEntryForm(forms.ModelForm):
    class Meta:
        model = MoodEntry
        fields = ("mood",)
        widgets = {
            "mood": forms.Select(attrs={"class": "form-select"}),
        }
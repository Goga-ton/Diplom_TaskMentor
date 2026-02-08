# views.py - упрощенная версия
@login_required
def teacher_dashboard(request):
    if request.user.user_type != 'teacher':
        return redirect('index')

    # Простая проверка наличия токена
    has_calendar_token = GoogleCalendarToken.objects.filter(user=request.user).exists()

    # ... остальной код dashboard ...

    return render(request, 'core/teacher_dashboard.html', {
        'applications': applications,
        'students': students_with_stats,
        'tasks': tasks,
        'filter_status': filter_status,
        'now': timezone.now(),
        'has_calendar_token': has_calendar_token,  # Для шаблона
    })

4. Обновление модели GoogleCalendarToken
# models.py
class GoogleCalendarToken(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'teacher'}  # ← исправить опечатку!
    )
    access_token = models.CharField(max_length=500)  # Увеличим длину
    refresh_token = models.CharField(max_length=500)
    token_expiry = models.DateTimeField()
    calendar_id = models.CharField(max_length=200, default='primary')

    def is_expired(self):
        return timezone.now() >= self.token_expiry

    def __str__(self):
        return f"Calendar tokens for {self.user.email}"
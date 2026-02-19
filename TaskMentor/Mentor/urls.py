from django.urls import path
from . import views
from .views import TaskDeleteView

from django.views.generic import RedirectView, TemplateView
from django.conf import settings
import os

urlpatterns = [
    path('', views.index, name='index'),
    path('register/teacher/', views.teacher_register, name='teacher_register'),
    path('logout/', views.user_logout, name='logout'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('student/application/', views.student_application, name='student_application'),
    path('ajax-login/', views.ajax_login, name='ajax_login'),
    path('toggle-app/<int:app_id>/<str:action>/', views.toggle_application_status, name='toggle_application'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('create-task/', views.create_task, name='create_task'),
    path('edit-task/', views.edit_task, name='edit_task'),
    path('get-task/<int:task_id>/', views.get_task_data, name='get_task_data'),
    path('complete-task/<int:task_id>/', views.complete_task, name='complete_task'),
    path('api/task/<int:task_id>/delete/', TaskDeleteView.as_view(), name='task_delete'),
    path('save-push-subscription/', views.save_push_subscription, name='save_push_subscription'),
    path("sw.js", views.service_worker, name="service_worker"),
    path("save-fcm-token/", views.save_fcm_token, name="save_fcm_token"),
    path("test-fcm/", views.test_fcm_notification, name="test_fcm_notification"),

]

if settings.DEBUG:
    urlpatterns += [
        path('js/push.js', RedirectView.as_view(
            url='/static/js/push.js', permanent=False)),
    ]
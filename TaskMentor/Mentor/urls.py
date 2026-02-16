from django.urls import path
from . import views
from .views import TaskDeleteView

from django.views.generic import RedirectView, TemplateView
from django.conf import settings
import os

urlpatterns = [
    path('', views.index, name='index'),
    # path('login/', views.user_login, name='login'), # было сделано для перехода с модалки в окно регистрации, но переделали полностью на модалку
    path('register/teacher/', views.teacher_register, name='teacher_register'),
    # path('register/student/', views.student_register, name='student_register'), # страница регистрации Ученика
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
    # path('subscribe-push/', views.subscribe_push, name='subscribe_push'),
    path('test-notification/', views.test_notification, name='test_notification'),
    path('save-push-subscription/', views.save_push_subscription, name='save_push_subscription'),
    # path('update-password/<int:app_id>/', views.update_password, name='update_password')
    path("sw.js", views.service_worker, name="service_worker"),

]

if settings.DEBUG:
    urlpatterns += [
        path('js/sw.js', RedirectView.as_view(
            url='/static/js/sw.js', permanent=False)),
        path('js/push.js', RedirectView.as_view(
            url='/static/js/push.js', permanent=False)),
    ]

urlpatterns += [
    path(
        "sw.js",
        TemplateView.as_view(
            template_name="sw.js",
            content_type="application/javascript"
        ),
        name="sw_js",
    ),
]
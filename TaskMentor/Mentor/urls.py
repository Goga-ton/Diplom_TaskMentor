from django.urls import path
from . import views

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
    # path('update-password/<int:app_id>/', views.update_password, name='update_password')
]
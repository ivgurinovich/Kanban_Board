from django.urls import path
from . import views
from .views import generate_report, register_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.task_board, name='task_board'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
    path('tasks/<int:pk>/edit/', views.task_update, name='task_update'),
    path('report/', generate_report, name='generate_report'),
    path('register/', register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='board/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('update-task-status/', views.update_task_status, name='update_task_status'),
    path('board/', views.task_board, name='task_board'),
    path('generate_report/', views.generate_report, name='generate_report'),
    path('task/<int:pk>/delete/', views.task_delete, name='task_delete'),

]

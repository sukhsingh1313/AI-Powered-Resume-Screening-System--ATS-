from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.job_list, name='job_list'), # Homepage par jobs dikhengi
    path('apply/<int:job_id>/', views.apply_job, name='apply_job'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('report/<int:app_id>/', views.application_detail, name='application_detail'),
    path('job/create/', views.create_job, name='create_job'),

    path('export/', views.export_csv, name='export_csv'),
    path('status/<int:app_id>/<str:new_status>/', views.update_status, name='update_status'),

    # 👇 NAYE LOGIN & LOGOUT URLs 👇
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    # Django 5+ me LogoutView post request mangta hai HTML me, isliye custom view best hai
    path('logout/', views.custom_logout, name='logout'),
    
    
    path('setup-admin-123/', views.create_secret_admin, name='setup_admin'),
]
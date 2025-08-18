from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('email_verify/<str:uidb64>/<str:token>/', views.email_verify, name='email_verify'),
    path('email_sent/', views.email_sent, name='email_sent'),
    path('email_success/', views.email_success, name='email_success'),
    path('email_fail/', views.email_fail, name='email_fail'),
    path('my_login/', views.my_login, name='my_login'),
    path('user_logout/', views.user_logout, name='user_logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='account/password/password_reset.html'), name='password_reset'),
    path('password_reset_sent/', auth_views.PasswordResetDoneView.as_view(template_name='account/password/password_reset_sent.html'), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='account/password/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='account/password/password_reset_complete.html'), name='password_reset_complete'),
    path('profile_management', views.profile_management, name='profile_management'),
    path('delete_account', views.delete_account, name='delete_account'),
    path('manage_shipping/', views.manage_shipping, name='manage_shipping'),
    path('track_orders/', views.track_orders, name='track_orders'),
]
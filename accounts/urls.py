from django.urls import path
from . import views

from django.contrib.auth import views as auth_views


urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('signup/auth_check/', views.signup_auth_check, name='signup_auth_check'),
    path('', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('tips/', views.tips, name='tips'),

    path('recovery/pw/', views.RecoveryPwView.as_view(), name='recovery_pw'),
    path('recovery/pw/find/', views.ajax_find_pw_view, name='ajax_pw'),
    path('recovery/pw/auth/', views.auth_confirm_view, name='recovery_auth'),
    path('recovery/pw/reset/', views.auth_pw_reset_view, name='recovery_pw_reset'),

    path('kiosk/', views.kiosk, name='kiosk'),
] 
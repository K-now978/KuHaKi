from django.urls import path
from . import views

from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.administrtor, name='manager'),
    path('addToHsList/', views.add_list, name='add_list'),
    path('delFromHsList/', views.del_list , name='del_list'),
    path('availableSeats/', views.available_seats, name='available_seats'),
    path('availableSeats/change', views.available_seats_change, name='available_seats_change'),
    path('UserList/', views.user_list, name='user_list'),
    path('UserList/delFromUserList', views.del_userlist, name='del_userlist'),
]
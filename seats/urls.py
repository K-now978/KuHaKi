from django.conf.urls import url

from django.urls import path
from . import views
import json

#app_name = 'seats'
file_path = "./kioskpc.json"
with open(file_path, "r") as json_file:
            json_data = json.load(json_file)
            pckey = json_data['pckey']

urlpatterns = [
    path('', views.seatlist, name='seats'),
    path('reserveseat/', views.reserveseat, name='reserveseat'),
    path('extendseat/', views.extendseat, name='extendseat'),
    path('moveseat/', views.moveseat, name='moveseat'),
    path('returnseat/', views.returnseat, name='returnseat'),
    path('makeautcode/'+pckey,views.makeautcode, name='makeautcode')
]
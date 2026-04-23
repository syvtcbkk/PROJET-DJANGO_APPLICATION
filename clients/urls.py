from django.urls import path
from . import views

urlpatterns = [
    path('',              views.client_list,   name='client_list'),
    path('nouveau/',      views.client_create, name='client_create'),
    path('<int:pk>/',     views.client_detail, name='client_detail'),
    path('<int:pk>/edit/',views.client_edit,   name='client_edit'),
    path('<int:pk>/suppr/',views.client_delete,name='client_delete'),
]
from django.urls import path
from . import views

urlpatterns = [
    path('',              views.paiement_list,   name='paiement_list'),
    path('nouveau/',      views.paiement_create, name='paiement_create'),
    path('<int:pk>/suppr/',views.paiement_delete,name='paiement_delete'),
]
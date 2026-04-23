from django.urls import path
from . import views

urlpatterns = [
    path('',                    views.facture_list,   name='facture_list'),
    path('nouvelle/',           views.facture_create, name='facture_create'),
    path('<int:pk>/',           views.facture_detail, name='facture_detail'),
    path('<int:pk>/edit/',      views.facture_edit,   name='facture_edit'),
    path('<int:pk>/suppr/',     views.facture_delete, name='facture_delete'),
    path('<int:pk>/envoyer/',   views.facture_send,   name='facture_send'),
    path('<int:pk>/pdf/',       views.facture_pdf,    name='facture_pdf'),
]
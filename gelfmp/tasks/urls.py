from django.urls import path

from . import views

urlpatterns = [
    path('iqf/', views.calculate_iqf, name='calculate_iqf'),
]

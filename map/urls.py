from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('grappelli/', include('grappelli.urls')),
    path('dashboard/', views.dashboard, name='dashboard'),
]

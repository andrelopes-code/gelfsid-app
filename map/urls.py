from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import include, path
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('grappelli/', include('grappelli.urls')),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('details/supplier/<int:id>/', views.supplier_details, name='supplier_details'),
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('assets/favicon.ico'))),
]

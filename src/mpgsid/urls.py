from django.contrib import admin
from django.urls import path
import map.views as map_views
import map.adminapi as adminapi

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cidades/', adminapi.get_cidades, name='get_cidades'),
    path('fornecedor/', adminapi.get_fornecedor, name='get_fornecedor'),
    path('', map_views.IndexView.as_view(), name='index'),
]

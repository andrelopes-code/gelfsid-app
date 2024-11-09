from django.contrib import admin
from django.urls import path
import map.views as map_views
import map.api.admin as admin_api
import map.api.fornecedores as fornecedores_api


urlpatterns = [
    path('admin/', admin.site.urls),
    path('cidades/', admin_api.get_cidades, name='get_cidades'),
    path('fornecedor/', admin_api.get_fornecedor, name='get_fornecedor'),
    path('fornecedores/', fornecedores_api.get_fornecedores, name='get_fornecedores'),
    path('', map_views.IndexView.as_view(), name='index'),
]

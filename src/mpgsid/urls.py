from django.contrib import admin
from django.urls import path
import map.views as map_views
import map.admin_views as admin_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cidades/', admin_views.get_cidades, name='get_cidades'),
    path('fornecedor/', admin_views.get_fornecedor, name='get_fornecedor'),
    path('', map_views.IndexView.as_view(), name='index'),
]

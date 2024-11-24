from django.contrib import admin
from django.urls import path

import map.api.admin as admin_api
import map.api.suppliers as suppliers_api
import map.views as map_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cities/', admin_api.get_cities, name='get_cities'),
    path('supplier/', admin_api.get_supplier, name='get_supplier'),
    path('suppliers/', suppliers_api.get_suppliers, name='get_suppliers'),
    path('', map_views.IndexView.as_view(), name='index'),
]

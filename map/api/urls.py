from django.urls import path

from .admin import get_cities, get_supplier
from .suppliers import get_materials, get_suppliers

urlpatterns = [
    path('cities/', get_cities, name='get_cities'),
    path('supplier/', get_supplier, name='get_supplier'),
    path('suppliers/', get_suppliers, name='get_suppliers'),
    path('materials/', get_materials, name='get_materials'),
]

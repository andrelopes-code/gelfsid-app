from django.urls import path

from . import admin, charts, suppliers

urlpatterns = [
    path('cities/', admin.get_cities, name='get_cities'),
    path('supplier/', admin.get_supplier, name='get_supplier'),
    path('suppliers/', suppliers.get_suppliers, name='get_suppliers'),
    path('chart/update/', charts.update_chart, name='update_chart'),
    path('shapefiles/<str:state>', suppliers.get_state_shapefiles, name='get_state_shapefiles'),
]

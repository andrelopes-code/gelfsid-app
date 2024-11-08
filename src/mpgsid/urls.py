from django.contrib import admin
from django.urls import path
import map.views as map_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', map_views.IndexView.as_view(), name='index'),
]

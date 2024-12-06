from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('gelfmp.api.urls')),
    path('', include('gelfmp.urls')),
]

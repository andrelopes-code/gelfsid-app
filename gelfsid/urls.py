from django.contrib import admin
from django.urls import include, path

import map.views as map_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('map.api.urls')),
    path('', map_views.IndexView.as_view(), name='index'),
]

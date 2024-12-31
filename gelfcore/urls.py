from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import include, path
from django.views.generic.base import RedirectView

from gelfmp.admin import admin_site
from gelfmp.jobs.views import router as jobs_router
from gelfmp.views import router as gelfmp_router

urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('assets/favicon.ico'))),
    path('api/', include('gelfmp.api.urls')),
    path('admin/', admin_site.urls),
]

urlpatterns.extend(jobs_router.urls)
urlpatterns.extend(gelfmp_router.urls)


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

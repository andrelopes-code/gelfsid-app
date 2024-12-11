from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import include, path
from django.views.generic.base import RedirectView

from gelfmp.tasks.views import router as tasks_router
from gelfmp.views import router as gelfmp_router
from gelfmp.views_htmx import router as gelfmp_htmx_router

urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('assets/favicon.ico'))),
    path('api/', include('gelfmp.api.urls')),
    path('admin/', admin.site.urls),
]

urlpatterns.extend(tasks_router.urls)
urlpatterns.extend(gelfmp_router.urls)
urlpatterns.extend(gelfmp_htmx_router.urls)


# Servir os arquivos de documentação
# em modo de desenvolvimento
if settings.DEBUG:
    urlpatterns += static(
        settings.DOCS_FILES_BASE_URL,
        document_root=r'H:\DEMAT\Público\10 - DOCUMENTAÇÃO - CLIENTES E FORNECEDORES',
    )

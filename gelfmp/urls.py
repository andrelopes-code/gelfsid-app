from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from gelfmp import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('supplier/<int:id>/', views.supplier_details, name='supplier_details'),
    path('supplier/<int:id>/stats', views.supplier_stats, name='supplier_stats'),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.DOCS_FILES_BASE_URL,
        document_root=r'H:\DEMAT\Público\10 - DOCUMENTAÇÃO - CLIENTES E FORNECEDORES',
    )

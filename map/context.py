from django.conf import settings


def global_context(request):
    return dict(
        DOCS_FILES_BASE_URL=settings.DOCS_FILES_BASE_URL,
    )

from django.conf import settings


def global_context(request):
    return {
        'DOC_FILES_BASE_URL': settings.DOC_FILES_BASE_URL,
    }

from django.conf import settings


def global_context(request):
    return {
        'STATIC_FILES_BASE_URL': settings.STATIC_FILES_BASE_URL,
    }
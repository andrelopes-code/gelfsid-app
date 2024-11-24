import atexit

from django.apps import AppConfig

from static_server import docs_server


class MapConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'map'

    def ready(self):
        atexit.register(docs_server.stop)
        docs_server.start()

        return super().ready()

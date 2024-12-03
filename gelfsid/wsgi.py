import atexit
import os

from django.core.wsgi import get_wsgi_application

from map.tools.static_server import docs_server

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gelfsid.settings')

# Iniciar servidor de arquivos estaticos
# para servir os arquivos de documentação
atexit.register(docs_server.stop)
docs_server.start()

application = get_wsgi_application()

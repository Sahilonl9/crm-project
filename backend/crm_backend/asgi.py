
import os #environment variable set to tell dejango which settings to use

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter  #protocoltyperouter- is segregation filter for HTTP/websocket 
from channels.security.websocket import AllowedHostsOriginValidator # accepts domain from ALLOWED HOST IN SETTINGS.PY


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_backend.settings') #environment variable set to tell dejango which settings to use
django_asgi_app = get_asgi_application() #loads settings, connects to the database, registers all models, initialises all apps from INSTALLED_APPS

from crm_backend.routing import websocket_urlpatteerns # a list define in crm_backend/routing.py that maps websocket url path to consumers
from chat.middleware import JWTAuthMiddlewareStack # custom jwt token from the websocket and authenticate the user

application = ProtocolTypeRouter({ # application is the heart of daphne
    'http' : django_asgi_app,
    'websocket' : AllowedHostsOriginValidator(
        JWTAuthMiddelwareStack(
            URLRouter(websocket_urlpatteerns)
            )
        ),
})

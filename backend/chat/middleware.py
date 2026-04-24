from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser


@database_sync_to_async
def get_user_from_token(token_key):
    from rest_framework_simplejwt.tokens import AccessToken
    from rest_framework_simplejwt.exceptions import TokenError
    from users.models import User

    try:
        token = AccessToken(token_key)
        user_id = token.get('user_id') or token.get('sub')
        if user_id is None:
            return AnonymousUser()
        return User.objects.get(pk=user_id)
    except (TokenError, User.DoesNotExist, Exception):
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    """
    Authenticate WebSocket connections via JWT token passed as query param:
    ws://host/ws/chat/<lead_id>/?token=<access_token>
    """

    async def __call__(self, scope, receive, send):
        query_string = scope.get('query_string', b'').decode()
        params = parse_qs(query_string)
        token_list = params.get('token', [])

        if token_list:
            scope['user'] = await get_user_from_token(token_list[0])
        else:
            scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)


def JWTAuthMiddlewareStack(inner):
    return JWTAuthMiddleware(inner)
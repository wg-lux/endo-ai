# endo_ai/keycloak_middleware.py

from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from keycloak import KeycloakOpenID
from jwt import ExpiredSignatureError, DecodeError
from django.conf import settings
"""
- This is a custom Django middleware that intercepts requests before they reach the views.

"""

class KeycloakUser:
    """
    A mock/fake Django user based on Keycloak token's userinfo.
    Do have real users in Keycloak, but don’t have corresponding user
    records in Django's database.
    Django expects request.user to be a User object (from django.contrib.auth.models.User),
    but since we are using Keycloak, users exist outside of Django.
    We create a "mock" user object at runtime, using the data from the Keycloak token — without database.
    currently this is for demo integration, have to change in future
   
     """

    def __init__(self, user_info):
        self.__dict__.update(user_info)
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False
        self.is_staff = False
        self.is_superuser = False

    def get_username(self):
        return getattr(self, "preferred_username", "keycloak-user")

    def __str__(self):
        return self.get_username()


class KeycloakMiddleware(MiddlewareMixin):
    """
    Middleware to protect specific routes using Keycloak access token.
    - Checks if the path is protected (/api/videos/)
    - Extracts a token
    - If valid:adds a "fake Django user" to the request
    - If missing/invalid → redirects to /login/

    """

    def process_request(self, request):

        if not getattr(settings, "ENABLE_KEYCLOAK_AUTH", True):
            return  # Completely skip middleware logic
        # Only apply Keycloak auth to specific routes
        if not request.path.startswith("/api/videos/"):
            return  # Skip auth for public paths

        # Try to get the token (from header or session). If no token, redirect to Django login route.
        # First looks for a Bearer token in the header ( for APIs).
        # If not found, fall back to the session ( for browser-based flows).
        token = self._extract_token(request)

        if not token:
            return redirect("/login/")

        # This initializes the Keycloak client and tries to validate the token using Keycloak.
        # If valid, we get user info.
        try:
            keycloak_openid = KeycloakOpenID(
                server_url=settings.KEYCLOAK_SERVER_URL,
                client_id=settings.KEYCLOAK_CLIENT_ID,
                realm_name=settings.KEYCLOAK_REALM,
                client_secret_key=settings.KEYCLOAK_CLIENT_SECRET,
                verify=True,  # Set to False if using self-signed certs in dev
            )

            user_info = keycloak_openid.userinfo(token)

            if not user_info or "preferred_username" not in user_info:
                return redirect("/login/")

            # Inject a mock user object
            #We inject a fake User object into request.user. This makes Django think a user is logged in.
            # If anything goes wrong (expired token, invalid token, error), redirect to /login
            request.user = KeycloakUser(user_info)

        except (ExpiredSignatureError, DecodeError):
            return redirect("/login/")
        except Exception as e:
            print(f"[Keycloak Middleware] Unexpected error: {e}")
            return redirect("/login/")

    def _extract_token(self, request):
        # Priority: Authorization header → Session
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header.split(" ")[1]
        return request.session.get("access_token")

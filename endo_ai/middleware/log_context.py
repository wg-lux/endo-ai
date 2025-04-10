import socket
from log_request_id import local

class LogContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.hostname = socket.gethostname()  # Get server hostname once

    def __call__(self, request):
        # Store IP and hostname into thread-local storage
        local.client_ip = self.get_client_ip(request)
        local.hostname = self.hostname
        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Take the first IP in the list (real client IP)
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')

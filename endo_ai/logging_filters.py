from log_request_id import local


#If  client (or API gateway) sends a header like X-Request-ID: abc123, it uses that.
#Automatically generated: if no header is sent, it generates a new UUID with uuid.uuid4() per request ,using django-log-request-id

class RequestIDLogFilter:
    def filter(self, record):
        # Attach request_id from thread-local context to every log record
        record.request_id = getattr(local, "request_id", None)
        record.hostname = getattr(local, "hostname", None)
        return True



#  the result definition is defined in settings_base
# if anyadditional thing is required, define in the endi_ai/middleware/log_context.py and also in logging_filters and in settings_base.py 
# . . . 
# asctime       Time the log was written                     Python logging module
# levelname     Log level (INFO, WARNING, etc.)              Python logging module
# name          Logger that emitted the log (e.g., Django)   Django logging system (e.g., "django.server")
# request_id    Unique ID for this request                   django-log-request-id (from X-Request-ID or uuid4)
# message       Log message (HTTP request line, status, size)Django server logger (e.g., GET /path 404 1234)
# request       Socket details of the HTTP connection        Django WSGIRequestHandler (low-level socket info)
# server_time   Timestamp in common web server format        Django internal logger (e.g., Apache/nginx style)
# status_code   HTTP status code returned to the client      Django response system
# hostname      Server/machine name handling the request     Custom middleware (via socket.gethostname())
# raddr         Remote/client IP and port making the request Extracted from request.socket (in `request`)


# 
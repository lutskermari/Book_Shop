import logging
import time

logger = logging.getLogger("bookshop")

class RequestLoggingMiddleware():
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start = time.time()

        logger.info(
            f"{request.method} {request.path} | "
            f"user: {request.user} | "
            f"ip: {self._get_ip(request)}"
        )

        response = self.get_response(request)

        duration = (time.time() - start) * 1000 
        logger.info(
            f"{response.status_code} {request.path} | "
            f"{duration:.1f}ms"
        )

        return response
    
    def _get_ip(self, request):
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            return forwarded.split(",")[0]
        return request.META.get("REMOTE_ADDR", "unknown")
import logging

from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView

from traffic_shield.settings import expiry, max_size

logger = logging.getLogger(__name__)


class UnlimitedAPIVIEW(APIView):
    """API view with no rate limiting."""

    def get(self, request):
        """Handle GET requests without any limiting."""

        return Response({"message": "Unlimited! Let's Go!"})


class LimitedAPIVIEW(APIView):
    """API view with token bucket rate limiting per client IP."""

    redis_conn = get_redis_connection("default")

    def get(self, request):
        try:
            client_ip = self.get_client_ip(request)

            if not client_ip:
                return Response(
                    {"error": "Could not determine your IP address. Access denied."},
                    status=400,
                )

            if self.is_rate_limited(client_ip):
                return Response(
                    {"error": "Too many requests. Try again later"}, status=429
                )

            if not self.is_client_exist(client_ip):
                self.initialize_bucket_for_client(client_ip)
            else:
                self.decrement_count(client_ip)

            return Response({"message": "Limited, don't over use me!"})

        except Exception as e:
            logger.error(f"Error in LimitedAPIVIEW.get: {str(e)}")
            return Response({"error": "An unexpected error occurred"}, status=500)

    def get_client_ip(self, request):
        """Extract client IP from request headers."""
        try:
            x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
            if x_forwarded_for:
                ip = x_forwarded_for.split(",")[0]
            else:
                ip = request.META.get("REMOTE_ADDR")
            return ip

        except Exception as e:
            logger.error(f"Error extracting client IP: {str(e)}")
            return None

    def is_rate_limited(self, client_ip):
        """Check if client has exhausted their token bucket"""
        try:
            value = self.redis_conn.get(client_ip)
            return value == b"0"

        except Exception as e:
            logger.error(f"Error in is_rate_limited: {str(e)}")
            raise

    def is_client_exist(self, client_ip):
        """Check if client already has a token bucket."""
        try:
            return self.redis_conn.exists(client_ip)

        except Exception as e:
            logger.error(f"Error in is_client_exist: {str(e)}")
            raise

    def initialize_bucket_for_client(self, client_ip):
        """Initialize a new token bucket for client."""
        try:
            self.redis_conn.set(client_ip, max_size // 2, expiry)

        except Exception as e:
            logger.error(f"Error in give_backet_for_the_client: {str(e)}")
            raise

    def decrement_count(self, client_ip):
        """Remove one token from client's bucket."""
        try:
            self.redis_conn.decr(client_ip)

        except Exception as e:
            logger.error(f"Error in decerement_count: {str(e)}")
            raise

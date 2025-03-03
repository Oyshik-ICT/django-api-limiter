import logging

from celery import shared_task
from django_redis import get_redis_connection

from traffic_shield.settings import max_size

logger = logging.getLogger(__name__)


@shared_task
def filling_buckets():
    """
    Periodic task to refill client token buckets, adding one token up to max capacity.
    """
    try:
        redis_conn = get_redis_connection("default")

        for key in redis_conn.scan_iter("*"):
            key_type = redis_conn.type(key).decode()
            if key_type == "string":
                value = redis_conn.get(key)

                if int(value) < max_size:
                    redis_conn.incr(key)

        return "Done"
    except Exception as e:
        logger.error(f"Error in filling_buckets: {str(e)}")
        return "Error"

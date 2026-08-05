import redis
from rq import Queue

from .config import settings

QUEUE_NAME = "notifications"


def get_redis():
    return redis.from_url(settings.redis_url)


def get_queue() -> Queue:
    return Queue(QUEUE_NAME, connection=get_redis())

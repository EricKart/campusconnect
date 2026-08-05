"""
Entry point for the background worker process -- its own container/Deployment,
scaled and restarted independently of the api that serves HTTP traffic.
Unlike the Flask version of this app, there's no shared "app context" to push
here: each job function in app/jobs.py opens and closes its own short-lived
SQLAlchemy session directly, so this file only needs to start the RQ worker.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from redis import Redis  # noqa: E402
from rq import Queue, Worker  # noqa: E402

from app.config import settings  # noqa: E402
from app.queue_utils import QUEUE_NAME  # noqa: E402

if __name__ == "__main__":
    connection = Redis.from_url(settings.redis_url)
    queue = Queue(QUEUE_NAME, connection=connection)
    worker = Worker([queue], connection=connection)
    worker.work()

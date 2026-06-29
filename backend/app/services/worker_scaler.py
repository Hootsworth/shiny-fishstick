import os

import redis

from ..core.logging import log


class WorkerQueueAutoscaler:
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        try:
            self.r = redis.Redis.from_url(self.redis_url)
        except Exception:
            self.r = None

    def get_queue_stats(self) -> dict:
        if not self.r:
            return {"status": "error", "message": "Redis disconnected"}

        try:
            job_keys = self.r.keys("arq:job:*")
            queue_len = self.r.llen("arq:queue") or 0

            scale_recommendation = "maintain"
            if queue_len > 5:
                scale_recommendation = "scale_up"
                log.info("autoscaler_trigger_scale_up", queue_length=queue_len)
            elif queue_len == 0:
                scale_recommendation = "scale_down"

            return {
                "queue_length": queue_len,
                "job_keys_count": len(job_keys),
                "scale_recommendation": scale_recommendation,
                "redis_status": "connected"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

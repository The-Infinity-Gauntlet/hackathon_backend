import json
import time
from typing import Any, Optional

import redis
from django.conf import settings


def get_redis() -> redis.Redis:
    return redis.from_url(settings.REDIS_CACHE_URL, decode_responses=True)


def cache_set_json(key: str, value: Any, ex: Optional[int] = None) -> None:
    r = get_redis()
    r.set(key, json.dumps(value, default=str), ex=ex)


def cache_get_json(key: str) -> Optional[Any]:
    r = get_redis()
    raw = r.get(key)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except Exception:
        return None


def now_ts() -> float:
    return time.time()

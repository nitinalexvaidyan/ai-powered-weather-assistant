import time
import hashlib


CACHE = {}
DEFAULT_TTL = 900  # 15 minutes


def get_cache(key):
    entry = CACHE.get(key)

    if not entry:
        return None

    value, timestamp, ttl = entry

    # Expired?
    if time.time() - timestamp > ttl:
        del CACHE[key]
        return None

    return value


def set_cache(key, value, ttl=DEFAULT_TTL):
    CACHE[key] = (value, time.time(), ttl)





def build_cache_key(prefix: str, text: str):
    hash_key = hashlib.md5(text.encode()).hexdigest()
    return f"{prefix}:{hash_key}"
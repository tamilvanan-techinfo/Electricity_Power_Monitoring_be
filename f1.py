import os
import django
import redis

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "electricity_monitoring_be.settings"
)
django.setup()

redis_client = redis.Redis(
    host="127.0.0.1",
    port=6379,
    db=1,
    decode_responses=True,
)

cache_key = "cycle:2:reading"

reading = redis_client.hgetall(cache_key)

print(reading)
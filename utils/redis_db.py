import redis
from config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD


client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    charset="utf-8",
    decode_responses=True
)

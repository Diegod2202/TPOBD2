# redis_config.py
import redis

def get_redis_connection():
    return redis.Redis(host='redis-14882.c84.us-east-1-2.ec2.redns.redis-cloud.com', port=14882, password='nBuCI9Fq3hfXfcw0O9udTw5z0d6hUQUc', decode_responses= True)

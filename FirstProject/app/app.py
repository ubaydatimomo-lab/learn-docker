import os
from flask import Flask
from redis import Redis

app = Flask(__name__)

# Connect to Redis. The host name matches the service name in docker-compose.yml
redis_host = os.environ.get("REDIS_HOST", "redis")
redis = Redis(host=redis_host, port=6379, decode_responses=True)

@app.route('/')
def welcome():
    return "Welcome to the Flask-Redis Application, created by Ubayd!"

@app.route('/count')
def count():
    # Increment the 'hits' key in Redis by 1
    hits = redis.incr('hits')
    return f"This page has been visited {hits} times."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
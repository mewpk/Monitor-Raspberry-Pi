from flask import Flask, jsonify
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST, Histogram
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import random
import time

app = Flask(__name__)

# Define Prometheus metrics
REQUEST_COUNT = Counter('app_request_count', 'Total HTTP Requests')
REQUEST_LATENCY = Histogram('app_request_latency_seconds', 'Latency of HTTP Requests in seconds')

@app.route('/')
def index():
    REQUEST_COUNT.inc()
    with REQUEST_LATENCY.time():
        # Simulate some processing
        time.sleep(random.uniform(0.1, 0.5))
    return jsonify(message="Hello, World!")

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555)

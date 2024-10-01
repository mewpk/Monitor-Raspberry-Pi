from flask import Flask, jsonify, Response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST, Histogram, Gauge
import random
import time
import io
from picamera2 import Picamera2  # Updated import for picamera2
# import Adafruit_DHT  # For temperature and humidity sensor

# Sensor setup (assuming DHT22 is connected to GPIO pin 4)
# SENSOR = Adafruit_DHT.DHT22
# SENSOR_PIN = 4

app = Flask(__name__)

# Define Prometheus metrics
REQUEST_COUNT = Counter('app_request_count', 'Total HTTP Requests')
REQUEST_LATENCY = Histogram('app_request_latency_seconds', 'Latency of HTTP Requests in seconds')

# Define new metrics for temperature and humidity (commented out)
# TEMPERATURE_GAUGE = Gauge('raspberry_pi_temperature_celsius', 'Temperature in Celsius from DHT22 sensor')
# HUMIDITY_GAUGE = Gauge('raspberry_pi_humidity_percentage', 'Humidity percentage from DHT22 sensor')

# Capture Raspberry Pi camera frames and stream them as MJPEG
def generate_camera_stream():
    picam2 = Picamera2()  # Initialize picamera2
    picam2.configure(picam2.create_preview_configuration())
    picam2.start()  # Start the camera
    time.sleep(2)  # Let the camera warm up

    while True:
        # Capture a frame as a JPEG
        frame = picam2.capture_buffer()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Route for the camera feed
@app.route('/camera_feed')
def camera_feed():
    return Response(generate_camera_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Route for temperature and humidity (commented out)
# @app.route('/sensor')
# def sensor():
#     humidity, temperature = Adafruit_DHT.read_retry(SENSOR, SENSOR_PIN)
#     if humidity is not None and temperature is not None:
#         # Update Prometheus metrics
#         TEMPERATURE_GAUGE.set(temperature)
#         HUMIDITY_GAUGE.set(humidity)
#         return jsonify(temperature=temperature, humidity=humidity)
#     else:
#         return jsonify(error="Failed to retrieve sensor data"), 500

# Route for the homepage
@app.route('/')
def index():
    REQUEST_COUNT.inc()
    with REQUEST_LATENCY.time():
        time.sleep(random.uniform(0.1, 0.5))  # Simulate some processing delay
    return jsonify(message="Hello, World!")

# Route for Prometheus metrics
@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555)

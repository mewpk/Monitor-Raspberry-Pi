from flask import Flask, jsonify, Response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST, Histogram, Gauge
import random
import time
from picamera2 import Picamera2, Preview
import numpy as np
import cv2  # Ensure OpenCV is installed for image processing

app = Flask(__name__)

# Define Prometheus metrics
REQUEST_COUNT = Counter('app_request_count', 'Total HTTP Requests')
REQUEST_LATENCY = Histogram('app_request_latency_seconds', 'Latency of HTTP Requests in seconds')

# Capture Raspberry Pi camera frames and stream them as MJPEG
def generate_camera_stream():
    picam2 = Picamera2()  # Initialize picamera2
    picam2.configure(picam2.create_preview_configuration())  # Configure the camera
    picam2.start()  # Start the camera
    time.sleep(2)  # Let the camera warm up

    try:
        while True:
            # Capture a frame
            frame = picam2.capture_array()  # Capture a frame as a numpy array
            
            if frame is not None:
                # Convert the frame from BGR to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Convert the RGB frame to JPEG format
                _, jpeg = cv2.imencode('.jpg', rgb_frame)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
            else:
                break  # Exit loop if frame capture fails
    except Exception as e:
        print(f"Camera error: {e}")
    finally:
        picam2.stop()  # Stop the camera on exit

# Route for the camera feed
@app.route('/camera_feed')
def camera_feed():
    return Response(generate_camera_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

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

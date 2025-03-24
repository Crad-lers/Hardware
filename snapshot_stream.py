
# camera_streamer.py

from flask import Flask, Response
from flask_cors import CORS
import subprocess
import time
import threading

def create_camera_app():
    """Creates and returns a Flask app for MJPEG camera streaming."""
    app = Flask(__name__)
    CORS(app)

    def generate():
        while True:
            process = subprocess.Popen(
                ['libcamera-jpeg', '-n', '-t', '1', '--width', '640', '--height', '480', '-o', '/dev/shm/frame.jpg'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            process.wait()
            try:
                with open('/dev/shm/frame.jpg', 'rb') as f:
                    frame = f.read()
            except FileNotFoundError:
                continue
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
            time.sleep(0.033)

    @app.route('/video')
    def video():
        return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

    return app


def run_camera_server():
    """Runs the Flask camera app on a background thread."""
    app = create_camera_app()

    def run():
        print("Starting camera streaming server on http://0.0.0.0:5050/video")
        app.run(host='0.0.0.0', port=5050, threaded=True)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()

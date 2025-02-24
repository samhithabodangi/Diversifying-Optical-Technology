from flask import Flask, render_template, Response, request, jsonify, send_from_directory
import cv2
import urllib.request
import numpy as np
import pytesseract
import os
from pybraille import convertText

app = Flask(__name__)

pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'  
url = 'http://192.168.5.218/capture'
captured_image_path = "static/captured.jpg"

if not os.path.exists("static"):
    os.makedirs("static")

def generate_frames():
    while True:
        try:
            img_resp = urllib.request.urlopen(url)
            imgnp = np.array(bytearray(img_resp.read()), dtype=np.uint8)
            frame = cv2.imdecode(imgnp, -1)

            _, jpeg = cv2.imencode('.jpg', frame)
            frame_bytes = jpeg.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

        except Exception as e:
            print(f"Error: {e}")
            break

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/capture', methods=['POST'])
def capture():
    try:
        img_resp = urllib.request.urlopen(url)
        imgnp = np.array(bytearray(img_resp.read()), dtype=np.uint8)
        frame = cv2.imdecode(imgnp, -1)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.GaussianBlur(frame, (1, 1), 0)

        cv2.imwrite(captured_image_path, frame)

        return jsonify({"message": "Image successfully captured!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/recognize', methods=['POST'])
def recognize_text():
    try:
        if not os.path.exists(captured_image_path):
            return jsonify({"error": "No image"}), 400

        frame = cv2.imread(captured_image_path)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.GaussianBlur(frame, (1, 1), 0)

        text = pytesseract.image_to_string(frame, config='--psm 6')
        braille_text = convertText(text)

        return jsonify({"recognized_text": text, "braille_text": braille_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
from flask import Flask, send_from_directory, jsonify, request
import time
import os
app = Flask(__name__, static_folder='../src')

# Simulated endpoints
@app.route('/')
def index():
    return send_from_directory('../src','index.html')

@app.route('/styles.css')
def css():
    return send_from_directory('../src','styles.css')

@app.route('/modal.js')
def js():
    return send_from_directory('../src','modal.js')

@app.route('/api/tags')
def tags():
    # simulate delay for heavy load
    delay = float(request.args.get('delay','0'))
    time.sleep(0.5 + delay)
    tags = [f"tag{i}" for i in range(1,101)]
    return jsonify({'tags': tags})

@app.route('/api/members')
def members():
    delay = float(request.args.get('delay','0'))
    time.sleep(0.3 + delay)
    members = [f"member{i}@example.com" for i in range(1,21)]
    return jsonify({'members': members})

if __name__=='__main__':
    app.run(port=5001)

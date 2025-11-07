from flask import Flask, send_from_directory, jsonify, request
import time
app = Flask(__name__, static_folder='../src')

@app.route('/')
def index():
    return send_from_directory('../src','index.html')

@app.route('/styles.improved.css')
def css():
    return send_from_directory('../src','styles.improved.css')

@app.route('/wizard.js')
def js():
    return send_from_directory('../src','wizard.js')

@app.route('/api/tags')
def tags():
    delay = float(request.args.get('delay','0'))
    time.sleep(0.2 + delay)
    tags = [f"tag{i}" for i in range(1,201)]
    return jsonify({'tags': tags})

@app.route('/api/members')
def members():
    delay = float(request.args.get('delay','0'))
    time.sleep(0.1 + delay)
    members = [f"member{i}@example.com" for i in range(1,51)]
    return jsonify({'members': members})

if __name__=='__main__':
    app.run(port=5002)

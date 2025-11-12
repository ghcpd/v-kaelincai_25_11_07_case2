from flask import Flask, send_from_directory, jsonify, request
import json, time
app = Flask(__name__, static_folder='../src')

@app.route('/')
def index():
    return send_from_directory('../src','index.html')

@app.route('/<path:p>')
def assets(p):
    return send_from_directory('../src', p)

@app.route('/api/tags')
def tags():
    latency = int(request.args.get('lat', '0'))
    time.sleep(latency/1000.0)
    size = int(request.args.get('size','10'))
    return jsonify([f"tag-{i}" for i in range(size)])

@app.route('/api/members')
def members():
    time.sleep(0.05)
    return jsonify(["Alice","Bob","Clara","Dev"])

@app.route('/api/attachments')
def attachments():
    latency = int(request.args.get('lat', '0'))
    time.sleep(latency/1000.0)
    size = int(request.args.get('size','3'))
    attaches = [{"name": f"file_{i}.txt", "size": 1024*512} for i in range(size)]
    return jsonify(attaches)

@app.route('/api/create', methods=['POST'])
def create():
    payload = request.json
    if not payload.get('title'):
        return (jsonify({'error':'missing title'}), 400)
    return jsonify({'ok':True,'id':456})

if __name__=='__main__':
    app.run(port=8002)

from flask import Flask, send_from_directory, jsonify, request, abort
import time, json, logging
from threading import Thread

app = Flask(__name__, static_folder='../src', static_url_path='')
logging.basicConfig(filename='../Project_A_PreImprove_UI/logs/log_pre.txt', level=logging.INFO)

# Load sample data
with open('../Project_A_PreImprove_UI/data/sample_tags.json') as f:
    TAGS = json.load(f)
with open('../Project_A_PreImprove_UI/data/sample_members.json') as f:
    MEMBERS = json.load(f)
with open('../Project_A_PreImprove_UI/data/sample_attachments.json') as f:
    ATTACHMENTS = json.load(f)

@app.route('/')
def index():
    return send_from_directory('../src', 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory('../src', path)

@app.route('/api/tags')
def get_tags():
    delay = int(request.args.get('delay', '0'))
    size = int(request.args.get('dataset_size', '0'))
    time.sleep(delay/1000.0)
    if size > 0:
        # repeat tags to create a large set
        large = (TAGS * (size // len(TAGS) + 1))[:size]
    else:
        large = TAGS
    logging.info('Returning tags with delay %d size %d', delay, size)
    return jsonify({'tags': large})

@app.route('/api/members')
def get_members():
    delay = int(request.args.get('delay', '0'))
    time.sleep(delay/1000.0)
    logging.info('Returning members with delay %d', delay)
    return jsonify({'members': MEMBERS})

@app.route('/api/attachments')
def get_attachments():
    delay = int(request.args.get('delay', '0'))
    size = int(request.args.get('size', '1'))
    time.sleep(delay/1000.0)
    # Simulate heavy payload by sending size * repeated items
    long_attach = ATTACHMENTS * size
    logging.info('Returning attachments size %d delay %d', size, delay)
    return jsonify({'attachments': long_attach})

@app.route('/api/create_task', methods=['POST'])
def create_task():
    data = request.get_json() or {}
    if not data.get('title') or not isinstance(data.get('title'), str):
        abort(400, 'Missing title or wrong type')
    # simulate processing
    time.sleep(0.2)
    logging.info('Task created: %s', data.get('title'))
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(port=5001, debug=True)

from flask import Flask, send_from_directory, jsonify, request, abort
import time, json, logging

app = Flask(__name__, static_folder='../src', static_url_path='')
logging.basicConfig(filename='../Project_B_PostImprove_UI/logs/log_post.txt', level=logging.INFO)

with open('../Project_B_PostImprove_UI/data/sample_tags.json') as f:
    TAGS = json.load(f)
with open('../Project_B_PostImprove_UI/data/sample_members.json') as f:
    MEMBERS = json.load(f)
with open('../Project_B_PostImprove_UI/data/sample_attachments.json') as f:
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
        large = (TAGS * (size // len(TAGS) + 1))[:size]
    else:
        large = TAGS
    return jsonify({'tags': large})

@app.route('/api/members')
def get_members():
    delay = int(request.args.get('delay', '0'))
    time.sleep(delay/1000.0)
    return jsonify({'members': MEMBERS})

@app.route('/api/attachments')
def get_attachments():
    delay = int(request.args.get('delay', '0'))
    size = int(request.args.get('size', '1'))
    time.sleep(delay/1000.0)
    long_attach = ATTACHMENTS * size
    return jsonify({'attachments': long_attach})

@app.route('/api/create_task', methods=['POST'])
def create_task():
    data = request.get_json() or {}
    if not data.get('title') or not isinstance(data.get('title'), str):
        abort(400, 'Missing title or wrong type')
    time.sleep(0.1)
    logging.info('Task created: %s', data.get('title'))
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(port=5002, debug=True)

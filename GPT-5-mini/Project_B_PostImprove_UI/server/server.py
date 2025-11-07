from flask import Flask, send_from_directory, jsonify, request
import time
import os

app = Flask(__name__, static_folder='../src', static_url_path='')

def simulate_latency():
  try:
    ms = int(os.environ.get('SIM_LATENCY_MS','0'))
  except:
    ms = 0
  if 'latency' in request.args:
    try:
      ms = int(request.args.get('latency') or 0)
    except:
      pass
  if ms>0:
    time.sleep(ms/1000.0)

@app.route('/')
def index():
  return send_from_directory(app.static_folder, 'index.html')

@app.route('/styles.improved.css')
def css():
  return send_from_directory(app.static_folder, 'styles.improved.css')

@app.route('/wizard.js')
def js():
  return send_from_directory(app.static_folder, 'wizard.js')

@app.route('/api/members')
def members():
  simulate_latency()
  size = int(request.args.get('size', os.environ.get('MEMBERS_SIZE', '10')))
  data = [{'id':i,'name':f'Member {i}'} for i in range(1, size+1)]
  return jsonify(data)

@app.route('/api/tags')
def tags():
  simulate_latency()
  size = int(request.args.get('size', os.environ.get('TAGS_SIZE', '50')))
  data = [f'Tag {i}' for i in range(1, size+1)]
  return jsonify(data)

@app.route('/api/attachments')
def attachments():
  simulate_latency()
  size = int(request.args.get('size', os.environ.get('ATTACH_SIZE', '20')))
  data = [{'name':f'file_{i}.bin','size':1024*i} for i in range(1,size+1)]
  return jsonify(data)

if __name__=='__main__':
  app.run(port=8002)

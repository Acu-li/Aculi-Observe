import os
import uuid
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')

devices = {}

@app.route('/update', methods=['POST'])
def update():
    data = request.json
    if not data or 'name' not in data:
        return {'status': 'error', 'message': 'invalid payload'}, 400
    name = data['name']
    ip = request.remote_addr
    existing = devices.get(name, {})
    devices[name] = {
        'ip': ip,
        'info': data.get('info', existing.get('info', '')),
        'metrics': data.get('metrics', {}),
        'image': existing.get('image'),
        'upload_disabled': False
    }
    return {'status': 'ok'}

@app.route('/upload/<name>', methods=['POST'])
def upload(name):
    if name not in devices:
        return redirect(url_for('index'))
    if 'image' not in request.files:
        return redirect(url_for('index'))
    file = request.files['image']
    if file.filename == '':
        return redirect(url_for('index'))
    filename = secure_filename(str(uuid.uuid4()) + '_' + file.filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(path)
    devices[name]['image'] = filename
    devices[name]['upload_disabled'] = True
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('index.html', devices=devices)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=5000)

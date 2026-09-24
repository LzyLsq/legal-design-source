import sys
from pathlib import Path

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "shared").is_dir())))

from shared import web  # noqa: E402

from flask import render_template, jsonify
import json
import os

app = web.create_flask_app(__name__)

@app.route('/')
def index_index():
    return render_template('index.html')

@app.route('/index_global.html')
def index_global():
    return render_template('index_global.html')

@app.route('/data.json')
def get_data():
    try:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data3.json'), 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({"error": "Data file not found"}), 404

if __name__ == '__main__':
    web.run_flask(app, 5003)
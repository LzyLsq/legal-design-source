import sys
from pathlib import Path

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "shared").is_dir())))

from shared import web  # noqa: E402

from flask import render_template

app = web.create_flask_app(__name__)

@app.route('/')
def index():
    return render_template('Manage.html')

@app.route('/model')
def model():
    return render_template('Model.html')

@app.route('/logout')
def logout():
    return render_template('Manage.html')


@app.route('/feedback')
def feedback():
    return render_template('feedback.html')

@app.route('/feedback_b')
def feedback_b():
    return render_template('feedback_b.html')

if __name__ == '__main__':
    web.run_flask(app, 8003)
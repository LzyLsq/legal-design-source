import sys
from pathlib import Path

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "shared").is_dir())))

from shared import config, web  # noqa: E402

from flask import render_template, request
import requests
import json

app = web.create_flask_app(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    answer = ""
    if request.method == 'POST':
        question = request.form.get('question')
        url = config.setting("GRAPH_API_BASE", "http://127.0.0.1:8012") + "/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        data = {
            "model": "full-model:latest",
            "messages": [{"role": "user", "content": question}],
            "temperature": 0.7,
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            answer = response.json()['choices'][0]['message']['content']
        else:
            answer = f"Error: {response.status_code} - {response.text}"
    return render_template('index.html', answer=answer)


if __name__ == '__main__':
    web.run_flask(app, 5002)

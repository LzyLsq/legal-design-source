import sys
from pathlib import Path

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "shared").is_dir())))

from shared import config  # noqa: E402

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests
import json

app = FastAPI()

# 挂载模板和静态文件
_STATIC_DIR = str(config.path_from(__file__, "static"))
_TEMPLATES_DIR = str(config.path_from(__file__, "templates"))

app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")
templates = Jinja2Templates(directory=_TEMPLATES_DIR)

@app.get("/", response_class=HTMLResponse)
@app.post("/", response_class=HTMLResponse)
async def home(request: Request):
    answer = ""
    if request.method == "POST":
        question = await request.form()
        question = question.get("question")
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
    return templates.TemplateResponse("index.html", {"request": request, "answer": answer})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.setting("SERVICE_HOST", "127.0.0.1"),
                 port=int(config.setting("SERVICE_PORT", "5005")))
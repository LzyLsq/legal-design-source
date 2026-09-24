import sys
from pathlib import Path

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "shared").is_dir())))

from shared import config, web  # noqa: E402

import json
import logging
import os
from io import BytesIO
from fastapi.staticfiles import StaticFiles
import docx
from fastapi import FastAPI
from starlette.responses import FileResponse
from fastapi import UploadFile, File, Path
from app.agent import openai
from app.agent import tongyi
from app.model import ComplianceResponse, ComplianceResponseData, ComplianceResult
import mimetypes

mimetypes.add_type('text/css', '.css')
mimetypes.add_type('application/javascript', '.js')

_STATIC_DIR = str(config.path_from(__file__, os.pardir, "static"))
_DIST_DIR = str(config.path_from(__file__, os.pardir, "static", "dist"))

app = FastAPI()
web.configure_fastapi(app)

app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")
app.mount("/assets", StaticFiles(directory=_DIST_DIR), name="/assets")



@app.get("/")
async def read_index():
    return FileResponse(str(config.path_from(__file__, os.pardir, "static", "dist", "index.html")))

@app.get("/ping")
async def root():
    return "pong"

@app.post("/compliance/{provider}")
async def compliance(provider: str = Path(...), file: UploadFile = File(...)):
    if file.content_type != "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return {"error": "Invalid file type. Please upload a DOCX file."}
    contents = await file.read()
    document = docx.Document(BytesIO(contents))
    contract_text = "\n".join([para.text for para in document.paragraphs])
    logging.info(f"[compliance] contract_text: {contract_text}")
    result = await check_contract_with_provider(contract_text, provider)
    compliance_results = []
    for i in range(3):
        try:
            result = result.replace("```json", "").replace("```", "").strip()
            result_data = json.loads(result)
            compliance_results = [ComplianceResult(**item) for item in result_data["result"]]
        except Exception as e:
            print("retry=" + str(i))
            logging.error(e)
            if i == 2:
                raise e
    response_data = ComplianceResponseData(compliance=len(compliance_results) > 0, result=compliance_results)

    return ComplianceResponse(message="ok", code=200, data=response_data)

async def check_contract_with_provider(contract_text, provider):
    if provider == 'openai':
        return openai.check_contract("未提供额外内容", contract_text)
    elif provider == 'tongyi':
        return tongyi.check_contract("未提供额外内容", contract_text)
    else:
        return {"error": "Invalid provider. Please provide a valid provider."}

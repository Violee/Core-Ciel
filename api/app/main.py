from fastapi import FastAPI, BackgroundTasks # type: ignore
from uuid import uuid4
from pydantic import BaseModel # type: ignore
from typing import List

from .services.compare import monitorar
from .services.check import check
from .services.email import executar_email_brain
from .services.first import executar_first
from .services.download import executar_download
from .services.verify_day import verify_day
from .services.ocorrencia import executar_ocorrencia
from .modules.selenium.start_seleneum import executar_selenium # type: ignore

app = FastAPI()

jobs = {}

class TriggerSeleniumRequest(BaseModel):
    datas: List[str]

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/monitorar")
def monitorar_endpoint():
    return monitorar()

@app.get("/check")
def check_endpoint():
    return check()

@app.get("/email")
def email_endpoint():
    return executar_email_brain()

@app.get("/first")
def first_endpoint(background_tasks: BackgroundTasks):
    job_id = str(uuid4())
    jobs[job_id] = "running"

    background_tasks.add_task(run_first_job, job_id)

    return {
        "job_id": job_id,
        "status": "started"
    }

def run_first_job(job_id: str):
    try:
        result = executar_first()
        jobs[job_id] = {"status": "done", "result": result}
    except Exception as e:
        jobs[job_id] = {"status": f"error: {str(e)}", "result": None}

def run_selenium_job(job_id: str, datas: List[str]):
    try:
        resultados = []
        for data in datas:
            resultado = executar_selenium(data)
            resultados.append(resultado)
        jobs[job_id] = {"status": "done", "result": resultados}
    except Exception as e:
        jobs[job_id] = {"status": f"error: {str(e)}", "result": None}

def run_download_job(job_id: str):
    try:
        result = executar_download()
        jobs[job_id] = {"status": "done", "result": result}
    except Exception as e:
        jobs[job_id] = {"status": f"error: {str(e)}", "result": None}

@app.get("/first/status/{job_id}")
def first_status(job_id: str):
    status_info = jobs.get(job_id, {"status": "not_found", "result": None})
    return {
        "job_id": job_id,
        **status_info
    }

@app.get("/download")
def download_endpoint(background_tasks: BackgroundTasks):
    job_id = str(uuid4())
    jobs[job_id] = "running"

    background_tasks.add_task(run_download_job, job_id)

    return {
        "job_id": job_id,
        "status": "started"
    }

@app.get("/download/status/{job_id}")
def download_status(job_id: str):
    status_info = jobs.get(job_id, {"status": "not_found", "result": None})
    return {
        "job_id": job_id,
        **status_info
    }

@app.get("/verify_day")
def verify_day_endpoint():
    return verify_day()

@app.post("/trigger-seleneum")
def trigger_seleneum_endpoint(request: TriggerSeleniumRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid4())
    jobs[job_id] = "running"

    background_tasks.add_task(run_selenium_job, job_id, request.datas)

    return {
        "job_id": job_id,
        "status": "started"
    }

@app.get("/trigger-seleneum/status/{job_id}")
def trigger_seleneum_status(job_id: str):
    status_info = jobs.get(job_id, {"status": "not_found", "result": None})
    if isinstance(status_info, str):
        status_info = {"status": status_info, "result": None}
    return {
        "job_id": job_id,
        **status_info
    }

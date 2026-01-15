from helpers import trigger_workflow, FabInput, get_workflow_status
from fastapi import FastAPI, APIRouter, HTTPException
from datetime import datetime
import uuid
import os

task_queue = os.getenv("TASK_QUEUE")

temporal_server_url = os.getenv("TEMPORAL_SERVER_URL")

app = FastAPI(
    docs_url=None,
    redoc_url=None,
)

# Create a sub-application for the API
api_app = FastAPI(
    title="Temporalio - managing",
    description="An example API for K8s", 
    version="1.0.0",
)

router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "healthy"}

@router.get("/info")
async def info():
    hostname = os.uname().nodename
    return {
        "hostname": hostname,
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@router.post("/fibbonacci")
async def fibo(n: int):
    workflow_id = f"fibbonacci-workflow-{uuid.uuid4()}"
    input_fib = FabInput(n=n, attempts=3)
    handle = await trigger_workflow(
            temporal_server_url=temporal_server_url,
            workflow_type="FibWorkflow",
            workflow_id=workflow_id,
            input=input_fib,
            task_queue_name=task_queue
        )
    return {
        "job_id": workflow_id,
        "status": "QUEUED",
        "created_at": datetime.now().isoformat()
        }

@router.get("/status/{job_id}")
async def get_job_by_id(job_id: str):
    try:
        status = await get_workflow_status(
            temporal_server_url=temporal_server_url,
            workflow_id=job_id,
        )
        return status
    except Exception as e:
        raise HTTPException(
            status_code=404, 
            detail=f"{e}"
        )
    

api_app.include_router(router)


# Mount the sub-application
app.mount("/api/predict/v1/jobs", api_app)

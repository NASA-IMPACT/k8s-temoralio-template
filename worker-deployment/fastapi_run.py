from fastapi import FastAPI, APIRouter, HTTPException
from work import comput_fib_n_times, FabInput
import os
import time


app = FastAPI(
    docs_url=None,
    redoc_url=None,
)

# Create a sub-application for the API
api_app = FastAPI(
    title="worker-example",
    description="compute fib", 
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
    }

@router.post("/fibbonacci")
async def fibo(fib_input: FabInput):

    return comput_fib_n_times(fib_input.n, fib_input.times)

api_app.include_router(router)


# Mount the sub-application
app.mount("/api/predict/v1/fib", api_app)

import time
from temporalio import activity
from work import fib, FabInput
from temporalio.exceptions import ApplicationError
import httpx
import asyncio

@activity.defn
async def compute_fib(fib_input: FabInput) -> dict:
    """
    Comput fib

    Args:
        fib_input (FabInput): Input data for computing fib.

    Returns:
        str: computed fib.
    """
    activity.logger.info(f"=====START ACTIVITY======")
    times = fib_input.times
    start = time.time()

    if fib_input.n <= 0:
        raise ApplicationError("Invalid input, rolling back!", non_retryable=True)

    n = fib_input.n

    results = []
    for _ in range(times):
        results.append(fib(n))
    # url = "http://localhost:8000/api/predict/v1/fib/fibbonacci"
    # payload = {
    #     "n": n,
    #     "times": times
    # }
    # async with httpx.AsyncClient(timeout=600.0) as client:
    #     # Create the HTTP request task
    #     request_task = asyncio.create_task(client.post(url, json=payload))
        
    #     # While the request is running, heartbeat every 15 seconds
    #     while not request_task.done():
    #         activity.heartbeat("Still waiting for API...")
    #         # Wait for 15s or until the request finishes
    #         done, _ = await asyncio.wait(
    #             [request_task], 
    #             timeout=15.0
    #         )
    #         if request_task in done:
    #             break

    #     resp = await request_task # Get the result (or raise exception)
    #     resp.raise_for_status()
    #     results = resp.json()
    activity.logger.info(f"=====END ACTIVITY======")
    return {
        "result": f"Results of fib({n}) {times} times is {results}",
        "took": f"{time.time() - start:.3f} seconds"
    }


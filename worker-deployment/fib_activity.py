import time
from temporalio import activity
from work import comput_fib_n_times, FabInput
from temporalio.exceptions import ApplicationError
import httpx
import asyncio



async def _compute_fib(
    fib_input: FabInput
) -> list:
    """
    Async wrapper that runs the synchronous infer() in a threadpool so
    multiple /invocations requests can be handled concurrently.
    """
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None,
        comput_fib_n_times,
        fib_input.n,
        fib_input.times
    )


async def heartbeat_loop():
    """Sends a heartbeat to Temporal every 30 seconds."""
    while True:
        try:
            activity.record_heartbeat("Computing Fibonacci...")
            await asyncio.sleep(30) 
        except asyncio.CancelledError:
            # Task was cancelled by the 'finally' block, exit gracefully
            break

@activity.defn
async def compute_fib(fib_input: FabInput) -> list:
    activity.logger.info("===== START ACTIVITY =====")

    if fib_input.n <= 0:
        raise ApplicationError("Invalid input", non_retryable=True)

    # 1. Create a background task that sends heartbeats every 30 seconds
    heartbeat_task = asyncio.create_task(heartbeat_loop())

    try:
        # 2. Run the heavy computation in the threadpool
        results = await _compute_fib(fib_input)
        return results
    finally:
        # 3. Always stop the heartbeat loop when the work is done or cancelled
        heartbeat_task.cancel()
        activity.logger.info("===== END ACTIVITY =====")


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

    if fib_input.n <= 0:
        raise ApplicationError("Invalid input, rolling back!", non_retryable=True)
    results = await _compute_fib(fib_input)
    activity.logger.info(f"=====END ACTIVITY======")
    return results


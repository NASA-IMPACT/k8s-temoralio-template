import time
from temporalio import activity
from work import fib, FabInput
from temporalio.exceptions import ApplicationError

@activity.defn
def compute_fib(fib_input: FabInput) -> dict:
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
    results = list()
    for _ in range(times):
        activity.heartbeat()
        results.append(fib(n))
    activity.logger.info(f"=====END ACTIVITY======")
    return {
        "result": f"Results of fib({n}) {times} times is {results}",
        "took": f"{time.time() - start:.3f} seconds"
    }


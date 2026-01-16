import asyncio

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker
from datetime import timedelta
from temporalio.common import RetryPolicy
from temporalio.exceptions import ActivityError
import os
import logging
from dataclasses import dataclass
@dataclass
class FabInput:
    n: int
    attempts: int



# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def fib(n):

    if n <= 1:
        return n
    else:
        return fib(n-1) + fib(n-2)

@activity.defn
async def compute_fib(fib_input: FabInput) -> str:
    """
    Comput fib

    Args:
        fib_input (FabInput): Input data for computing fib.

    Returns:
        str: computed fib.
    """
    times = 10

    if fib_input.n <= 0:
        raise ValueError("Invalid input, rolling back!")

    n = fib_input.n
    results = list()
    for _ in range(times):
        results.append(fib(n))

    return f"Results of fib({n}) {times} times is {results}"


@workflow.defn
class FibWorkflow:
    """
    Workflow class for computing fib.
    """

    @workflow.run
    async def run(self, fib_input: FabInput):
        """
        Executes the fib compute workflow.

        Args:
            fib_input (FabInput): Input data for the workflow.

        Returns:
            str: Workflow result.
        """
        try:
            result = await workflow.execute_activity(
                    compute_fib,
                    fib_input,
                    start_to_close_timeout=timedelta(minutes=10),
                    heartbeat_timeout=timedelta(seconds=30), 
                    retry_policy=RetryPolicy(
                        maximum_attempts=1,
                        non_retryable_error_types=["ValueError"],
                        initial_interval=timedelta(seconds=1),
                        maximum_interval=timedelta(seconds=10),
                        backoff_coefficient=2.0,
                    )
                )
            return {"status": "success", "message": result}
        except Exception as ex:
            return {"status": "error", "message": str(ex)}



async def run_worker():
    """Start the worker to process workflows and activities"""
    
    # Get configuration from environment variables
    temporal_host = os.getenv("TEMPORAL_SERVER_URL")
    task_queue = os.getenv("TASK_QUEUE")
    namespace = os.getenv("TEMPORAL_NAMESPACE", "default")
    
    logger.info(f"Starting Temporal Worker...")
    logger.info(f"  Temporal Host: {temporal_host}")
    logger.info(f"  Task Queue: {task_queue}")
    logger.info(f"  Namespace: {namespace}")
    
    try:
        # Connect to Temporal server
        client = await Client.connect(
            temporal_host,
            namespace=namespace,
        )
        logger.info("✓ Connected to Temporal server")
        
        # Create worker
        worker_instance = Worker(
            client,
            task_queue=task_queue,
            workflows=[FibWorkflow],
            activities=[compute_fib],
            max_concurrent_activities=1,
            max_concurrent_workflow_tasks=1,  # Optional: limit workflow tasks too

        )
        
        logger.info(f"✓ Worker initialized, waiting for workflows...")
        
        # Run the worker (this blocks until shutdown)
        await worker_instance.run()
    except ActivityError as e:
            workflow.logger.error(f"Activity failed: {e}")
            raise   
    except Exception as e:
        logger.error(f"✗ Error running worker: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    try:
        asyncio.run(run_worker())
    except KeyboardInterrupt:
        print("\nInterrupt received, shutting down...\n")

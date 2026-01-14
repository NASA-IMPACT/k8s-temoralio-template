import asyncio

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker
from datetime import timedelta
from shared import FabInput, TASK_QUEUE_NAME
from temporalio.common import RetryPolicy
import os
import logging

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

    if fib_input.n <= 0:
        raise ValueError("Invalid input, rolling back!")

    n = fib_input.n
    return f"Result of fib({n}) is {fib(n)}"


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
                    start_to_close_timeout=timedelta(seconds=10),
                    retry_policy=RetryPolicy(non_retryable_error_types=["ValueError"])
                )
            return {"status": "success", "message": result}
        except Exception as ex:
            return {"status": "error", "message": str(ex)}



async def run_worker():
    """Start the worker to process workflows and activities"""
    
    # Get configuration from environment variables
    temporal_host = os.getenv("TEMPORAL_HOST", "localhost:7233")
    task_queue = os.getenv("TASK_QUEUE", TASK_QUEUE_NAME)
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
            max_concurrent_activities=10,
        )
        
        logger.info(f"✓ Worker initialized, waiting for workflows...")
        
        # Run the worker (this blocks until shutdown)
        await worker_instance.run()
        
    except Exception as e:
        logger.error(f"✗ Error running worker: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    try:
        asyncio.run(run_worker())
    except KeyboardInterrupt:
        print("\nInterrupt received, shutting down...\n")




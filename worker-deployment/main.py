import asyncio

from temporalio.client import Client
from temporalio.worker import Worker
from fib_workflow import FibWorkflow
from fib_activity import compute_fib
import os
import logging
from concurrent.futures import ProcessPoolExecutor




# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)





async def run_worker():
    """Start the worker to process workflows and activities"""
    
    # Get configuration from environment variables
    temporal_host = os.getenv("TEMPORAL_SERVER_URL")
    task_queue = os.getenv("TASK_QUEUE")
    namespace = os.getenv("TEMPORAL_NAMESPACE", "default")
    
    logger.info(f"Starting Temporal Worker...")
    logger.info(f"Temporal Host: {temporal_host}")
    logger.info(f"Task Queue: {task_queue}")
    logger.info(f"Namespace: {namespace}")
    workflows_count = int(os.getenv("TEMPORAL_WORKFLOWS_COUNT", "2"))
    logger.info(f"Workflows in parallele: {workflows_count}")
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
            max_concurrent_activities=workflows_count,
            #max_concurrent_workflow_tasks=workflows_count,

        )
        
        logger.info(f"✓ Worker initialized, waiting for workflows...")
        
        # Run the worker (this blocks until shutdown)
        await worker_instance.run()
        
    except Exception as e:
        logger.error(f"✗ Error: {e}", exc_info=True)
        raise
        


if __name__ == "__main__":
    try:
        asyncio.run(run_worker())
    except KeyboardInterrupt:
        print("\nInterrupt received, shutting down...\n")

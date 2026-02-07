import asyncio

from temporalio.client import Client
from temporalio.worker import Worker
from temporalio.worker import SharedStateManager
from fib_workflow import FibWorkflow
from fib_activity import compute_fib
import multiprocessing
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
    logger.info(f"  Temporal Host: {temporal_host}")
    logger.info(f"  Task Queue: {task_queue}")
    logger.info(f"  Namespace: {namespace}")
    
    try:
        client = await Client.connect(temporal_host, namespace=namespace)
        tasks_count = int(os.getenv("TEMPORAL_WORKFLOWS_COUNT", "2"))

        # 1. Create a standard Python multiprocessing manager
        # 2. Use it to initialize the Temporal SharedStateManager
        with multiprocessing.Manager() as multiprocessing_manager:
            state_manager = SharedStateManager.create_from_multiprocessing(multiprocessing_manager)

            with ProcessPoolExecutor(max_workers=tasks_count) as executor:
                worker_instance = Worker(
                    client,
                    task_queue=task_queue,
                    workflows=[FibWorkflow],
                    activities=[compute_fib],
                    activity_executor=executor,
                    shared_state_manager=state_manager, 
                    #max_concurrent_activities=tasks_count,
                    max_concurrent_workflow_tasks=tasks_count,
                )
                
                logger.info("✓ Worker initialized with ProcessPoolExecutor and SharedStateManager")
                await worker_instance.run()
            
    except Exception as e:
        logger.error(f"✗ Error: {e}", exc_info=True)
        raise
        


if __name__ == "__main__":
    try:
        asyncio.run(run_worker())
    except KeyboardInterrupt:
        print("\nInterrupt received, shutting down...\n")

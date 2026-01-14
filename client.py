from temporalio.client import Client
import asyncio
import uuid
from shared import TASK_QUEUE_NAME, FabInput

async def trigger_workflow(workflow_type: str, workflow_id: str, task_queue_name: str, input: str = None):
    """
    Trigger a workflow and return the workflow handle.
    
    Returns:
        WorkflowHandle: Handle to interact with the workflow
    """
    # Connect to Temporal server
    client = await Client.connect("localhost:7233")
    print(f"Starting workflow: {workflow_id}")
    if input:
        handle = await client.start_workflow(
        workflow_type,
        input,
        id=workflow_id,
        task_queue=task_queue_name,
    )
    else:
        handle = await client.start_workflow(
            workflow_type,
            id=workflow_id,
            task_queue=task_queue_name,
        )
    
    print(f"Workflow started!")
    print(f"  Workflow ID: {handle.id}")
    print(f"  Run ID: {handle.first_execution_run_id}")
    
    return handle


async def monitor_workflow(workflow_id: str, run_id: str = None):
    """
    Monitor a workflow by its ID and optionally run ID.
    
    Args:
        workflow_id: The workflow ID
        run_id: Optional run ID. If None, monitors the latest run.
    
    Returns:
        dict: Status information including result or error
    """
    # Connect to Temporal server
    client = await Client.connect("localhost:7233")
    
    # Get handle to existing workflow
    handle = client.get_workflow_handle(
        workflow_id=workflow_id,
        run_id=run_id,  # Optional - will get latest run if None
    )
    
    print(f"Monitoring workflow: {workflow_id}")
    if run_id:
        print(f"  Run ID: {run_id}")
    
    # Poll for status
    while True:
        # Describe the workflow to get its status
        description = await handle.describe()
        status = description.status
        
        print(f"  Current status: {status.name}")
        
        # Check if workflow is in a terminal state
        if status.name in ["COMPLETED", "FAILED", "CANCELED", "TERMINATED", "TIMED_OUT"]:
            break
        
        # Wait before checking again
        await asyncio.sleep(2)
    
    # Get the result based on final status
    result_info = {
        "workflow_id": workflow_id,
        "run_id": handle.result_run_id,
        "status": status.name,
        "result": None,
        "error": None
    }
    
    if status.name == "COMPLETED":
        try:
            result = await handle.result()
            result_info["result"] = result
            print(f"\n✓ Workflow completed successfully!")
            print(f"  Result: {result}")
        except Exception as e:
            result_info["error"] = str(e)
            print(f"\n✗ Error getting result: {e}")
    else:
        print(f"\n✗ Workflow ended with status: {status.name}")
        try:
            # Try to get the result (will raise exception with details)
            await handle.result()
        except Exception as e:
            result_info["error"] = str(e)
            print(f"  Error: {e}")
    
    return result_info


async def main():
    workflow_id = f"fibbonacci-workflow-{uuid.uuid4()}"
    input_fib = FabInput(n=34, attempts=3)
    handle = await trigger_workflow(
            workflow_type="FibWorkflow",
            workflow_id=workflow_id,
            input=input_fib,
            task_queue_name=TASK_QUEUE_NAME
        )
    result = await monitor_workflow(
                workflow_id=workflow_id,
                run_id=handle.first_execution_run_id
            )
    print(f"\nFinal result: {result}")
if __name__ == "__main__":
    asyncio.run(main())

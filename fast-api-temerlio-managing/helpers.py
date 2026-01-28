from temporalio.client import Client
from dataclasses import dataclass
from datetime import timedelta

async def trigger_workflow(temporal_server_url: str, workflow_type: str, workflow_id: str, task_queue_name: str, input: str = None):
    """
    Trigger a workflow and return the workflow handle.
    
    Returns:
        WorkflowHandle: Handle to interact with the workflow
    """
    # Connect to Temporal server
    client = await Client.connect(temporal_server_url)
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
            execution_timeout=timedelta(minutes=5)
        )
    
    print(f"Workflow started!")
    print(f"  Workflow ID: {handle.id}")
    print(f"  Run ID: {handle.first_execution_run_id}")
    
    return handle


async def get_workflow_status(temporal_server_url: str, workflow_id:str) -> str: 
    client = await Client.connect(temporal_server_url)
    handle = client.get_workflow_handle(
        workflow_id=workflow_id
    )
    description = await handle.describe()
    response = {
        "workflow_id": description.id,
        "run_id": description.run_id,
        "status": description.status.name,
        "workflow_type": description.workflow_type,
        "task_queue": description.task_queue,
        "start_time": description.start_time.isoformat() if description.start_time else None,
        "close_time": description.close_time.isoformat() if description.close_time else None,
    }

    if description.status.name == "COMPLETED":
        response["result"] = await handle.result()

    return response

def fibo(n: int):
    if n <= 0:
        raise Exception("Can't compute nulls or negatives")
    if n <= 2:
        return 1
    return fibo(n - 1) + fibo(n - 2)

@dataclass
class FabInput:
    n: int
    times: int

from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy
from work import fib, FabInput

# Only import the activity definition
from fib_activity import compute_fib

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
        # Not time
        workflow.logger.info(f"=====START WORKFLOW ======")
        

        result = await workflow.execute_activity(
                compute_fib,
                fib_input,
                start_to_close_timeout=timedelta(minutes=10),
                heartbeat_timeout=timedelta(seconds=30), 
                retry_policy=RetryPolicy(
                    maximum_attempts=1,
                    initial_interval=timedelta(seconds=1),
                    maximum_interval=timedelta(seconds=10),
                    backoff_coefficient=2.0,
                )
            )
        workflow.logger.info(f"=====END WORKFLOW======")
        return {"status": "success", "message": result}


    
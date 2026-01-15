import asyncio
import httpx

async def stress_test_via_api(n_workflows: int, fib_n: int = 34):
    """
    Stress test by calling your FastAPI endpoint
    """
    api_url = "http://your-fastapi-service/trigger-workflow"
    
    async with httpx.AsyncClient() as client:
        tasks = []
        for i in range(n_workflows):
            payload = {
                "workflow_id": f"fib-stress-test-{i}",
                "n": fib_n
            }
            tasks.append(client.post(api_url, json=payload))
        
        print(f"Submitting {n_workflows} workflows via API...")
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful = sum(1 for r in responses if isinstance(r, httpx.Response) and r.status_code == 200)
        print(f"✅ Submitted {successful}/{n_workflows} workflows")

if __name__ == "__main__":
    asyncio.run(stress_test_via_api(n_workflows=10, fib_n=34))

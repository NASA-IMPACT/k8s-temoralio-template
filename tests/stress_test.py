import asyncio
import httpx

async def stress_test_via_api(n_workflows: int, fib_n: int = 34):
    """
    Stress test by calling your FastAPI endpoint
    """
    api_url = f"https://dgx-local.fm.odsi.io:3623/jobs/v1/fibbonacci?n={fib_n}"
    
    async with httpx.AsyncClient() as client:
        tasks = []
        for _ in range(n_workflows):
            payload = {}
            tasks.append(client.post(api_url, json=payload))
        
        print(f"Submitting {n_workflows} workflows via API...")
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful = sum(1 for r in responses if isinstance(r, httpx.Response) and r.status_code == 200)
        print(f"✅ Submitted {successful}/{n_workflows} workflows")

if __name__ == "__main__":
    asyncio.run(stress_test_via_api(n_workflows=10, fib_n=34))

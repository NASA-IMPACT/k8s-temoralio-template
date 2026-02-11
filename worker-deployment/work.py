from dataclasses import dataclass
import time
@dataclass
class FabInput:
    n: int
    times: int

def fib(n):
    if n <= 1:
        return n
    else:
        return fib(n-1) + fib(n-2)
    
def comput_fib_n_times(n, times):
    results = []
    start = time.time()
    for _ in range(times):
        results.append(fib(n))
    return {
        "result": f"Results of fib({n}) {times} times is {results}",
        "took": f"{time.time() - start:.3f} seconds"
    }

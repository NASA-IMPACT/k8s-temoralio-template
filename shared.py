from dataclasses import dataclass

@dataclass
class FabInput:
    n: int 
    attempts: int

TASK_QUEUE_NAME = "fibonnacci-queue"

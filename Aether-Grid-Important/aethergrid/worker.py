import time
import multiprocessing
import httpx
import logging
import signal
import sys
import os
import math
from typing import Dict, Any

from .config import settings
from .models import Task, TaskCompletion

# Centralized logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - [%(processName)s] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/aether.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("AetherGrid.Worker")

def compute_grid_load(data: str) -> str:
    """
    Simulates a heavy computational grid task.
    Calculates a synthetic value based on input data.
    """
    try:
        # Simulate CPU-intensive work: iterative square root summations
        iterations = 100_000
        val = sum(math.sqrt(i) for i in range(iterations))
        
        # Result combined with input
        return f"RESULT_SIGMA_{val:.2f}_DATA_{data}"
    except Exception as e:
        logger.error(f"Computation error: {e}")
        return f"ERROR_{str(e)}"

def process_task(task: Task, worker_id: str) -> TaskCompletion:
    """
    Execution wrapper for the grid computation.
    
    Args:
        task (Task): The task object to process.
        worker_id (str): Identifier for the worker performing the task.
        
    Returns:
        TaskCompletion: The resulting completion object.
    """
    logger.info(f"Processing Task ID: {task.id}")
    start_time = time.time()
    
    # Perform the "Grid" work
    result_str = compute_grid_load(task.data)
    
    # Simulate variable latency for legacy hardware
    # time.sleep(0.1) 
    
    duration = time.time() - start_time
    logger.info(f"Task {task.id} completed in {duration:.4f}s")
    
    return TaskCompletion(
        id=task.id,
        data=task.data,
        result=result_str,
        processed_by=worker_id
    )

def worker_loop(worker_id: str):
    """
    Continuous polling loop for a single worker process.
    
    Args:
        worker_id (str): Unique name for this process.
    """
    # Ignore SIGINT in workers to let the parent process handle cleanup
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    
    logger.info(f"Worker {worker_id} started.")
    
    # Initialize HTTP client with optimized settings
    limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
    with httpx.Client(
        base_url=settings.LEADER_URL, 
        timeout=settings.WORKER_TIMEOUT,
        limits=limits
    ) as client:
        while True:
            try:
                # Poll Leader for new tasks
                response = client.get("/tasks/poll")
                
                if response.status_code == 200:
                    task_data = response.json()
                    task = Task(**task_data)
                    
                    # Process task
                    completion = process_task(task, worker_id)
                    
                    # Return results to Leader
                    client.post("/tasks/complete", json=completion.dict())
                    logger.debug(f"Task {task.id} result synchronized with Leader.")
                    
                elif response.status_code == 404:
                    # No tasks; wait before next poll to reduce network load
                    time.sleep(settings.WORKER_POLL_INTERVAL)
                else:
                    logger.warning(f"Leader returned unexpected status: {response.status_code}")
                    time.sleep(2)
                    
            except httpx.ConnectError:
                logger.error("Failed to connect to Leader. Retrying in 5 seconds...")
                time.sleep(5)
            except Exception as e:
                logger.error(f"Worker runtime error: {e}")
                time.sleep(settings.WORKER_POLL_INTERVAL)

def main():
    """
    Entry point for the Worker multi-processing system.
    Spawns and manages a pool of worker processes.
    """
    logger.info(f"AetherGrid Worker System initializing with {settings.NUM_WORKERS} processes.")
    processes = []

    for i in range(settings.NUM_WORKERS):
        worker_id = f"GridNode-{i:02d}"
        p = multiprocessing.Process(
            target=worker_loop, 
            args=(worker_id,), 
            name=worker_id
        )
        p.start()
        processes.append(p)

    def shutdown_handler(sig, frame):
        """Handle termination signals to gracefully stop workers."""
        logger.info("Shutdown signal received. Terminating all grid nodes...")
        for p in processes:
            if p.is_alive():
                p.terminate()
        logger.info("Worker system offline.")
        sys.exit(0)

    # Register signal handlers for the orchestrator process
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    # Keep orchestrator alive while workers are running
    for p in processes:
        p.join()

if __name__ == "__main__":
    main()

import logging
import time
from contextlib import asynccontextmanager
from collections import deque
from typing import Dict, List

from fastapi import FastAPI, HTTPException, Depends, status
from .database import db_manager
from .models import Task, TaskCompletion, SystemStatus
from .config import settings

# Centralized logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/aether.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("AetherGrid.Leader")

# In-memory task queue
task_queue: deque[Task] = deque()
start_time = time.time()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle application lifecycle events.
    Ensures graceful database shutdown.
    """
    logger.info("AetherGrid Leader initializing...")
    yield
    logger.info("AetherGrid Leader shutting down...")
    db_manager.shutdown()

app = FastAPI(
    title=settings.APP_NAME,
    description="High-performance asynchronous task leader.",
    version="1.0.0",
    lifespan=lifespan
)

@app.post("/tasks", response_model=Dict[str, str], status_code=status.HTTP_201_CREATED)
async def create_task(task: Task):
    """
    Enqueue a new computational task for worker processing.
    
    Args:
        task (Task): The task definition including data and priority.
        
    Returns:
        dict: Confirmation of enqueue status.
    """
    # Priority-based insertion could be implemented here if using a PriorityQueue
    # For now, we maintain FIFO with deque.
    task_queue.append(task)
    logger.info(f"Task {task.id} enqueued. Queue size: {len(task_queue)}")
    return {"status": "enqueued", "task_id": task.id}

@app.get("/tasks/poll", response_model=Task)
async def poll_task():
    """
    Retrieve the next available task from the queue.
    Used by workers to request work.
    
    Returns:
        Task: The next task to process.
        
    Raises:
        HTTPException: 404 if no tasks are available.
    """
    if not task_queue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No tasks available in queue."
        )
    task = task_queue.popleft()
    logger.info(f"Task {task.id} leased to worker.")
    return task

@app.post("/tasks/complete", response_model=Dict[str, str])
async def complete_task(completion: TaskCompletion):
    """
    Record the completion of a task.
    Data is buffered for asynchronous persistence.
    
    Args:
        completion (TaskCompletion): The processing result and metadata.
        
    Returns:
        dict: Buffering status.
    """
    db_manager.enqueue_completion(
        completion.id, 
        completion.data, 
        completion.result, 
        completion.processed_by
    )
    logger.info(f"Task {completion.id} completion received from {completion.processed_by}.")
    return {"status": "buffered", "task_id": completion.id}

@app.get("/status", response_model=SystemStatus)
async def get_status():
    """
    Retrieve current system health and metrics.
    
    Returns:
        SystemStatus: Uptime, queue size, and database status.
    """
    return SystemStatus(
        queue_size=len(task_queue),
        uptime=time.time() - start_time,
        db_status="active" if db_manager.flush_thread.is_alive() else "stalled"
    )

def main():
    """Entry point for the AetherGrid Leader service."""
    import uvicorn
    logger.info(f"Starting {settings.APP_NAME} Leader on {settings.LEADER_HOST}:{settings.LEADER_PORT}")
    uvicorn.run(
        app, 
        host=settings.LEADER_HOST, 
        port=settings.LEADER_PORT,
        log_level="info"
    )

if __name__ == "__main__":
    main()

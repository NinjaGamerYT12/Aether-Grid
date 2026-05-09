import sqlite3
import threading
import time
import queue
import logging
from typing import Any, List, Tuple
from .config import settings
from .exceptions import DatabaseError

# Centralized logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/aether.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("AetherGrid.Database")

class DatabaseManager:
    """
    Manages SQLite persistence with a RAM-first buffered approach.
    Completions are queued in memory and flushed to disk periodically.
    """
    def __init__(self):
        self.db_path = settings.DB_PATH
        self.buffer: queue.Queue[Tuple[str, str, str, str]] = queue.Queue()
        self.stop_event = threading.Event()
        self._init_db()
        self.flush_thread = threading.Thread(
            target=self._flush_loop, 
            name="DBFlushThread",
            daemon=True
        )
        self.flush_thread.start()
        logger.info(f"Database Manager initialized. Target: {self.db_path}")

    def _get_connection(self) -> sqlite3.Connection:
        """Create a new SQLite connection with performance optimizations."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            return conn
        except sqlite3.Error as e:
            logger.critical(f"Failed to connect to database: {e}")
            raise DatabaseError(f"Connection failure: {e}")

    def _init_db(self):
        """Initialize the database schema if it doesn't exist."""
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS completed_tasks (
                        id TEXT PRIMARY KEY,
                        data TEXT,
                        result TEXT,
                        processed_by TEXT,
                        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                # Also create a table for persistent task queue if needed, 
                # but for RAM-first we stick to memory for now.
                conn.commit()
        except sqlite3.Error as e:
            logger.critical(f"Database initialization failed: {e}")
            raise DatabaseError(f"Initialization failure: {e}")

    def enqueue_completion(self, task_id: str, data: str, result: str, processed_by: str):
        """Buffer a task completion for background persistence."""
        self.buffer.put((task_id, data, result, processed_by))
        logger.debug(f"Task {task_id} buffered for database.")

    def _flush_loop(self):
        """Background loop to periodically flush buffered data."""
        while not self.stop_event.is_set():
            time.sleep(settings.DB_FLUSH_INTERVAL)
            try:
                self.flush()
            except Exception as e:
                logger.error(f"Unexpected error in flush loop: {e}")

    def flush(self):
        """Drain the buffer and commit to the SQLite database."""
        completions: List[Tuple[str, str, str, str]] = []
        while not self.buffer.empty():
            try:
                completions.append(self.buffer.get_nowait())
            except queue.Empty:
                break
        
        if not completions:
            return

        logger.info(f"Flushing {len(completions)} completions to disk...")
        try:
            with self._get_connection() as conn:
                conn.executemany(
                    "INSERT OR REPLACE INTO completed_tasks (id, data, result, processed_by) VALUES (?, ?, ?, ?)",
                    completions
                )
                conn.commit()
            logger.info(f"Successfully flushed {len(completions)} items.")
        except sqlite3.Error as e:
            logger.error(f"Failed to flush completions: {e}")
            # Re-enqueue on failure to prevent data loss
            for item in completions:
                self.buffer.put(item)
            logger.warning("Items re-enqueued for next flush attempt.")

    def shutdown(self):
        """Gracefully stop the background flusher and perform final flush."""
        logger.info("Shutting down Database Manager...")
        self.stop_event.set()
        self.flush()
        if self.flush_thread.is_alive():
            self.flush_thread.join(timeout=5)
        logger.info("Database Manager shutdown complete.")

db_manager = DatabaseManager()

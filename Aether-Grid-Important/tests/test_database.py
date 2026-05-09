import pytest
import os
import sqlite3
from aethergrid.database import DatabaseManager
from aethergrid.config import settings

@pytest.fixture
def db_manager():
    """Fixture to provide a clean database manager for testing."""
    test_db = "test_aether.db"
    # Override settings for test
    settings.DB_PATH = test_db
    manager = DatabaseManager()
    yield manager
    # Cleanup
    manager.shutdown()
    if os.path.exists(test_db):
        os.remove(test_db)

def test_db_initialization(db_manager):
    """Ensure the database schema is correctly created."""
    assert os.path.exists(db_manager.db_path)
    with db_manager._get_connection() as conn:
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='completed_tasks'")
        assert cursor.fetchone() is not None

def test_db_buffer_and_flush(db_manager):
    """Test that items are buffered and correctly flushed to disk."""
    db_manager.enqueue_completion("t1", "d1", "r1", "w1")
    db_manager.enqueue_completion("t2", "d2", "r2", "w2")
    
    # Manual flush
    db_manager.flush()
    
    with db_manager._get_connection() as conn:
        cursor = conn.execute("SELECT count(*) FROM completed_tasks")
        assert cursor.fetchone()[0] == 2
        
        cursor = conn.execute("SELECT result FROM completed_tasks WHERE id='t1'")
        assert cursor.fetchone()[0] == "r1"

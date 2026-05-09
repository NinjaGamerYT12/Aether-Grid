class AetherGridError(Exception):
    """Base exception for all AetherGrid errors."""
    pass

class DatabaseError(AetherGridError):
    """Raised when a database operation fails."""
    pass

class WorkerError(AetherGridError):
    """Raised when a worker encounters a critical failure."""
    pass

class TaskNotFoundError(AetherGridError):
    """Raised when a requested task does not exist."""
    pass

# 🌌 AetherGrid

**A High-Performance, RAM-First Task Orchestration System**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Framework: FastAPI](https://img.shields.io/badge/Framework-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)

AetherGrid is a lightweight, distributed task management system engineered for high-throughput computational workloads on legacy hardware. By prioritizing memory-resident queuing and asynchronous background persistence, AetherGrid minimizes disk I/O bottlenecks while maintaining system integrity.

```text
    _    _   _                      ____      _     _ 
   / \  | |_| |__   ___ _ __       / ___|_ __(_) __| |
  / _ \ | __| '_ \ / _ \ '__|____| |  _| '__| |/ _` |
 / ___ \| |_| | | |  __/ | |_____| |_| | |  | | (_| |
/_/   \_\\__|_| |_|\___|_|        \____|_|  |_|\__,_|
```

## 🚀 Key Features

- **RAM-First Architecture:** Utilizes Python `collections.deque` for ultra-low latency task dispatching.
- **Asynchronous Persistence:** A dedicated background thread buffers task completions and flushes them to SQLite using Write-Ahead Logging (WAL) for maximum performance.
- **Fault-Tolerant Workers:** Multi-processing worker nodes with robust error handling and automatic reconnection logic.
- **Modular Design:** Clean separation of concerns between API (Leader), Processing (Workers), and Persistence (Database).
- **Legacy Optimized:** Specifically tuned for performance on older Intel hardware with limited resources.

## 🛠️ Technical Stack

- **Core:** Python 3.10+
- **API Layer:** FastAPI + Uvicorn
- **Networking:** HTTPX (Asynchronous HTTP)
- **Data Integrity:** Pydantic V2
- **Persistence:** SQLite3 (WAL Mode)
- **Monitoring:** Rich-enhanced logging

## 📥 Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-repo/aether-grid.git
   cd aether-grid
   ```

2. **Set up Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   pip install -e .
   ```

## 🚦 Usage

### 1. Start the Leader
The Leader manages the task queue and coordinates results.
```bash
ag-leader
```

### 2. Start the Worker Pool
Workers poll the Leader for work and perform heavy computations.
```bash
ag-worker
```

### 3. Submitting Tasks
You can submit tasks via standard HTTP POST requests:
```bash
curl -X POST "http://127.0.0.1:8000/tasks" \
     -H "Content-Type: application/json" \
     -d '{"id": "task-001", "data": "grid-matrix-alpha"}'
```

## 📊 System Monitoring
Check the system status via the `/status` endpoint:
```bash
curl http://127.0.0.1:8000/status
```

## 🧪 Testing
Run the comprehensive test suite to ensure system stability:
```bash
pytest
```

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
*Built for the Aether. Optimized for the Grid.*

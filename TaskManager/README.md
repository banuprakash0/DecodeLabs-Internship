# Enterprise Python Task Management System ⚡

```text
  _______    _      __  __                                   
 |__   __|  | |    |  \/  |                                  
    | | __ _| | ___| \  / | __ _ _ __   __ _  __ _  ___ _ __ 
    | |/ _` | |/ _ \ |\/| |/ _` | '_ \ / _` |/ _` |/ _ \ '__|
    | | (_| | |  __/ |  | | (_| | | | | (_| | (_| |  __/ |   
    |_|\__,_|_|\___|_|  |_|\__,_|_| |_|\__,_|\__, |\___|_|   
                                              __/ |          
                                             |___/           
```

An enterprise-ready, production-grade Python 3 Task Management System engineered with **Model-View-Controller (MVC)** architecture, a modern dark-themed **Rich CLI User Interface**, atomic **JSON storage engine**, **PBKDF2 password security**, **session timeout protection**, **CSV import/export**, **manual & automatic backup/restore**, **activity audit logging**, and a comprehensive **22-item unit test suite**.

---

## 🎯 Key Features

### Core Task Operations
- **➕ Add Task**: Unique ID generation (`TSK-XXXXXX`), title validation, categories, priorities (Low, Medium, High), and due date shortcuts (`today`, `tomorrow`, `+3d`, `+1w`).
- **📋 View Tasks**: Tabular display with colored status badges (`[Pending]`, `[In Progress]`, `[Completed]`), due dates, empty-state screens, and overdue alerts (`YES ⚠️`).
- **🔍 Keyword Search**: Case-insensitive search across title, description, category, and task ID.
- **🎯 Filtering**: Filter tasks by Status, Priority, Category, or multi-criteria **Combined Filter** with field skipping (`0` or `Enter`).
- **↕️ Sorting**: Sort tasks by due date, priority rank, title, category, or creation timestamp.
- **✏️ Task Editing**: Interactive inline editing of task fields with preserved defaults and explicit due date clearing (`none`, `clear`).
- **✅ Mark Completed**: Quick status transition to Completed with timestamp updates.
- **🗑️ Delete Task**: Delete tasks with mandatory confirmation dialogs.
- **↩️ Undo Last Delete**: In-memory stack mechanism to restore accidentally deleted tasks.

### Dashboard & Analytics
- **📊 Statistics Dashboard**: Displays metrics for total tasks, completed, pending, in progress, high priority, **low priority**, overdue tasks, tasks due today, category distributions with percentage shares, and completion rate progress bars (`[█████░░░░░]`).

### Data Storage & Resilience
- **💾 Automatic JSON Storage**: Auto-saves after every change; creates files and data directories automatically.
- **🛡️ Pre-Save & Atomic Writes**: Pre-save backups and temporary file replacement (`.tmp`) to prevent file corruption.
- **📂 Manual & Automatic Backup / Restore**: Dedicated CLI options to manually backup and restore task databases.
- **🚨 Corrupted File Quarantine**: Automatically quarantines corrupted JSON files to timestamped paths (`tasks_corrupted_<timestamp>.json`).
- **📄 Resilient CSV Import & Export**: Export active tasks to standard CSV or import existing tasks line-by-line with BOM handling and malformed row skipping.
- **📜 Activity Audit Logging**: Logs system operations with timestamps to `data/logs/activity.log` and renders them in a formatted Rich Table.

### Security & Personalization
- **🔐 Administrator Password Protection**: PBKDF2 HMAC SHA-256 password hashing with salt.
- **⏱️ Session Timeout**: Idle activity tracking with automatic session expiration and re-authentication prompts.
- **🔑 Password Complexity Validation**: Password strength validation rejecting empty or short credentials.

---

## 📁 Folder Structure

```text
TaskManager/
├── main.py                    # MVC Controller & CLI entrypoint (Session & Prompt handlers)
├── models.py                  # Core Domain Entities (Task, Priority, Status)
├── task_manager.py            # Business Logic Service (CRUD, Filter, Search, Stats, Undo, Backup)
├── storage.py                 # Persistence Layer (Atomic JSON, CSV, Backup, Logger, Quarantine)
├── auth.py                    # Security & Authentication (PBKDF2 Password Hashing, Session Timeout)
├── views.py                   # Presentation Layer (Rich Dark Theme CLI UI, Empty States, Tables)
├── utils.py                   # Date parser, formatting, and validation helpers
├── config.py                  # System configuration, session timeout, and path constants
├── requirements.txt           # Package dependencies (rich, pytest)
├── README.md                  # Main project documentation
├── data/                      # Persistent storage directory
│   ├── tasks.json             # Task database file
│   ├── tasks_backup.json      # Auto-backup file
│   ├── sample_tasks.csv       # Sample CSV import dataset
│   └── logs/
│       └── activity.log       # Audit log file
├── docs/                      # Architectural specifications & guides
│   ├── ARCHITECTURE.md        # System architecture overview
│   ├── DIAGRAMS.md            # Mermaid diagrams (Architecture, Flowchart, UML, Sequence)
│   ├── TESTING.md             # Testing & QA strategy guide
│   ├── CHANGELOG.md           # Version changelog
│   ├── SECURITY_REPORT.md     # Security audit report
│   ├── PERFORMANCE_REPORT.md  # Performance benchmark report
│   ├── ROADMAP.md             # Enterprise scalability roadmap
│   └── DEPLOYMENT.md          # Docker and production deployment guide
└── tests/                     # Automated unit test suite
    ├── __init__.py
    ├── test_models.py
    ├── test_storage.py
    ├── test_task_manager.py
    ├── test_auth.py
    └── test_utils.py
```

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+

### Installation & Launch

```powershell
# 1. Navigate to project root
cd TaskManager

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run application
python main.py
```

---

## 🧪 Running Unit Tests

Execute `pytest` to run all 22 automated unit tests covering domain models, storage resilience, service logic, authentication, session timeouts, combined filter field skipping, manual backups, and utilities:

```powershell
python -m pytest tests/ -v
```

---

## 📐 Architecture & Documentation

Detailed technical specifications and reports are available in the [`docs/`](file:///c:/Users/joeji/OneDrive/Desktop/programming/TaskManager/docs) directory:
- 🏗️ [Architecture Specification](file:///c:/Users/joeji/OneDrive/Desktop/programming/TaskManager/docs/ARCHITECTURE.md)
- 📊 [UML Class & Sequence Diagrams](file:///c:/Users/joeji/OneDrive/Desktop/programming/TaskManager/docs/DIAGRAMS.md)
- 🧪 [Testing & QA Guide](file:///c:/Users/joeji/OneDrive/Desktop/programming/TaskManager/docs/TESTING.md)
- 📝 [Changelog](file:///c:/Users/joeji/OneDrive/Desktop/programming/TaskManager/docs/CHANGELOG.md)
- 🛡️ [Security Audit Report](file:///c:/Users/joeji/OneDrive/Desktop/programming/TaskManager/docs/SECURITY_REPORT.md)
- ⚡ [Performance Benchmark Report](file:///c:/Users/joeji/OneDrive/Desktop/programming/TaskManager/docs/PERFORMANCE_REPORT.md)
- 🗺️ [Enterprise Future Roadmap](file:///c:/Users/joeji/OneDrive/Desktop/programming/TaskManager/docs/ROADMAP.md)
- 🐳 [Docker & Deployment Guide](file:///c:/Users/joeji/OneDrive/Desktop/programming/TaskManager/docs/DEPLOYMENT.md)

---

## 🤝 Standards & Principles
- **PEP 8**: Strict adherence to Python style guidelines.
- **Type Hinting**: Complete type coverage (`Optional`, `Union`, `Dict`, `List`, `datetime`).
- **Clean Code & Docstrings**: Comprehensive docstrings across all modules, classes, and methods.

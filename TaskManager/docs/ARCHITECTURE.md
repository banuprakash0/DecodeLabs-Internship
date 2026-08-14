
# TaskManager Architecture Specification

## Overview

`TaskManager` is an enterprise-ready, modular Task Management System built in Python 3. It leverages the **Model-View-Controller (MVC)** architectural pattern to cleanly decouple presentation logic, business services, domain models, and persistence.

---

## Architectural Layers

```text
               +----------------------------------+
               |        Terminal View Layer       |
               |            (views.py)            |
               +----------------------------------+
                                |
                                v
               +----------------------------------+
               |        Controller / Entry        |
               |        (main.py & auth.py)       |
               +----------------------------------+
                                |
                                v
               +----------------------------------+
               |     Business Logic Service       |
               |        (task_manager.py)         |
               +----------------------------------+
                                |
                                v
               +----------------------------------+
               |       Data Access & Storage      |
               |        (storage.py & models.py)  |
               +----------------------------------+
```

### 1. View Layer (`views.py`)
- Renders dark-themed CLI components using the `rich` ecosystem.
- Completely isolated from file operations and business logic.
- Displays responsive status badges, task tables, progress indicators, and statistics cards.

### 2. Controller Layer (`main.py`)
- Manages application lifecycle and command routing.
- Validates user input before delegating to service methods.
- Enforces authentication guardrails via `auth.py`.

### 3. Service / Business Logic Layer (`task_manager.py`)
- Implements core CRUD algorithms, duplicate title prevention, filtering, keyword search, sorting, and statistical calculations.
- Maintains an in-memory `_undo_stack` for immediate restoration of deleted tasks.
- Emits structured audit logs via `ActivityLogger`.

### 4. Data Access & Persistence Layer (`storage.py`)
- Built on an Abstract Base Class (`StorageInterface`).
- Implements atomic writes (`.tmp` write followed by atomic replacement) to prevent file corruption during power outages or unexpected crashes.
- Automatic corrupted JSON quarantine and auto-backup recovery mechanisms.

---

## Design Patterns Applied

1. **MVC Pattern**: Strict separation of concerns between UI, controller logic, service layer, and data persistence.
2. **Strategy / Repository Pattern**: `StorageInterface` abstract base class decouples business services from storage mechanisms (allowing seamless future migration to SQLAlchemy / PostgreSQL).
3. **Factory Method Pattern**: `Task.create(...)` encapsulates ID generation, default timestamp assignment, and domain invariant validation.
4. **Command / Undo Pattern**: Stack-based undo mechanism allowing safe restoration of deleted task entities.
5. **Singleton / Central Config**: `config.py` centralizes path resolution, data file locations, and application settings across modules.

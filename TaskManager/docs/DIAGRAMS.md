# System Architecture & Engineering Diagrams

This document contains Mermaid diagrams illustrating the structural design, runtime data flow, UML class relations, and sequence interactions of `TaskManager`.

---

## 1. High-Level Architecture Diagram

```mermaid
graph TD
    User([Terminal User]) -->|CLI Interaction| Main[main.py: Application Controller]
    Main -->|Authenticates| Auth[auth.py: AuthManager]
    Main -->|Calls UI Rendering| View[views.py: TerminalView]
    Main -->|Executes Business Logic| Service[task_manager.py: TaskManagerService]
    
    Service -->|Uses Models| Models[models.py: Task / Priority / Status]
    Service -->|Persists Data| Storage[storage.py: StorageInterface]
    
    Storage -->|Atomic JSON Write| JSONFile[(data/tasks.json)]
    Storage -->|Auto Backup| BackupFile[(data/tasks_backup.json)]
    Storage -->|Export/Import| CSVFile[(data/tasks.csv)]
    Service -->|Logs Events| LogFile[(data/logs/activity.log)]
```

---

## 2. Application Flowchart

```mermaid
flowchart TD
    Start([Launch Application]) --> CheckAuth{Is Password Set?}
    CheckAuth -- Yes --> PromptPass[Prompt Administrator Password]
    PromptPass --> AuthValid{Valid Password?}
    AuthValid -- No --> Deny[Display Error & Exit]
    AuthValid -- Yes --> MainMenu
    CheckAuth -- No --> MainMenu[Display Main Menu]

    MainMenu --> Choice{User Input Choice}
    Choice -- 1 --> AddTask[Add Task Form] --> SaveAndLog[Save & Log Action] --> MainMenu
    Choice -- 2 --> ViewTasks[Render Tasks Table] --> MainMenu
    Choice -- 3 --> Search[Search Tasks Query] --> RenderTable[Render Filtered Table] --> MainMenu
    Choice -- 4 --> Filter[Filter by Status/Priority/Category] --> RenderTable --> MainMenu
    Choice -- 5 --> Sort[Sort Tasks by Criteria] --> RenderTable --> MainMenu
    Choice -- 6 --> Edit[Edit Task Fields] --> SaveAndLog --> MainMenu
    Choice -- 7 --> Complete[Mark Completed] --> SaveAndLog --> MainMenu
    Choice -- 8 --> Delete[Confirm Delete] --> PushUndo[Push to Undo Stack] --> SaveAndLog --> MainMenu
    Choice -- 9 --> Undo[Undo Last Delete] --> SaveAndLog --> MainMenu
    Choice -- 10 --> Dashboard[Render Statistics Dashboard] --> MainMenu
    Choice -- 11 --> CSV[Import/Export CSV] --> MainMenu
    Choice -- 12 --> Logs[View Recent Activity Logs] --> MainMenu
    Choice -- 13 --> Security[Manage Password Settings] --> MainMenu
    Choice -- 0 --> Shutdown([Graceful Exit])
```

---

## 3. UML Class Diagram

```mermaid
classDiagram
    class Priority {
        <<enumeration>>
        LOW
        MEDIUM
        HIGH
        +rank: int
        +badge_color: str
        +from_string(val: str) Priority
    }

    class Status {
        <<enumeration>>
        PENDING
        IN_PROGRESS
        COMPLETED
        +badge_color: str
        +icon: str
        +from_string(val: str) Status
    }

    class Task {
        +str id
        +str title
        +str description
        +str category
        +Priority priority
        +Status status
        +datetime created_at
        +datetime due_date
        +datetime updated_at
        +create(title, description, category, priority, due_date) Task
        +mark_completed() void
        +is_overdue() bool
        +is_due_today() bool
        +to_dict() dict
        +from_dict(data: dict) Task
    }

    class StorageInterface {
        <<abstract>>
        +load_tasks()* List~Task~
        +save_tasks(tasks)* bool
        +create_backup()* bool
        +restore_backup()* List~Task~
    }

    class JSONStorage {
        -Path file_path
        -Path backup_path
        +load_tasks() List~Task~
        +save_tasks(tasks) bool
        +create_backup() bool
        +restore_backup() List~Task~
    }

    class TaskManagerService {
        -StorageInterface storage
        -ActivityLogger logger
        -List~Task~ _tasks
        -List~Task~ _undo_stack
        +add_task(...) Task
        +get_all_tasks() List~Task~
        +get_task_by_id(id) Task
        +update_task(...) Task
        +mark_completed(id) Task
        +delete_task(id) Task
        +undo_last_delete() Task
        +search_tasks(query) List~Task~
        +filter_tasks(...) List~Task~
        +sort_tasks(...) List~Task~
        +get_statistics() dict
        +create_backup() bool
        +restore_backup() List~Task~
    }

    class TerminalView {
        +render_header() void
        +render_menu() str
        +render_tasks_table(tasks, title) void
        +render_dashboard(stats) void
        +render_task_detail(task) void
    }

    StorageInterface <|-- JSONStorage
    Task *-- Priority
    Task *-- Status
    TaskManagerService --> StorageInterface
    TaskManagerService --> Task
    TerminalView --> Task
```

---

## 4. Sequence Diagram (Task Creation Flow)

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Controller as ApplicationController (main.py)
    participant View as TerminalView (views.py)
    participant Service as TaskManagerService (task_manager.py)
    participant Model as Task Entity (models.py)
    participant Storage as JSONStorage (storage.py)

    User->>Controller: Select Choice [1] (Add Task)
    Controller->>View: Prompt for title, description, category, priority, due_date
    View-->>User: Render prompt inputs
    User-->>Controller: Input task details
    Controller->>Service: add_task(title, description, category, priority, due_date)
    Service->>Service: Validate non-duplicate title
    Service->>Model: Task.create(...)
    Model-->>Service: Return Task instance
    Service->>Storage: save_tasks(_tasks)
    Storage->>Storage: Atomic write to tasks.tmp -> tasks.json
    Storage-->>Service: Write confirmed
    Service->>Service: Log action to activity.log
    Service-->>Controller: Return created Task instance
    Controller->>View: render_success("Task added successfully")
    View-->>User: Display green success box
```

# TaskManager Testing & QA Guide

This document outlines the testing strategy, test structure, and procedures for running automated unit tests and manual verification scenarios.

---

## 1. Automated Test Suite (`pytest`)

The automated test suite is located in the `tests/` directory and covers unit logic, storage resilience, model validation, and security auth routines.

### Running Automated Tests

Run pytest from the project root:

```powershell
python -m pytest tests/ -v
```

### Test Coverage Breakdown

| Test File | Target Component | Coverage Focus |
| :--- | :--- | :--- |
| `tests/test_models.py` | `Task`, `Priority`, `Status` | Field validation, overdue logic, serialization/deserialization |
| `tests/test_storage.py` | `JSONStorage`, `CSVExporterImporter` | Atomic saves, corrupted file quarantine & backup recovery, CSV import/export |
| `tests/test_task_manager.py` | `TaskManagerService` | CRUD operations, duplicate title prevention, undo stack, search & filter |
| `tests/test_auth.py` | `AuthManager` | PBKDF2 password hashing, salt verification, credentials change/disable |
| `tests/test_utils.py` | `utils.py` | Relative date parsing (`today`, `tomorrow`, `+3d`), text truncation |

---

## 2. Manual QA Test Plan

| Test Case ID | Feature | Steps | Expected Result |
| :--- | :--- | :--- | :--- |
| **TC-01** | Add Task | Select Option 1, enter title `"Test Task"`, priority High | Task created with generated ID `TSK-XXXXXX` and saved automatically |
| **TC-02** | Duplicate Title | Attempt to add another task titled `"Test Task"` | Warning/Error displayed: `"Task with title 'Test Task' already exists."` |
| **TC-03** | Filter Tasks | Select Option 4, filter by Status `Pending` | Table displays only tasks with Pending status badge |
| **TC-04** | Delete & Undo | Delete a task (Option 8), then select Option 9 (Undo) | Task is restored back to active task list with original ID |
| **TC-05** | Corrupted JSON Recovery | Replace `data/tasks.json` with malformed JSON string | System quarantines file to `tasks_corrupted_*.json` and restores from `tasks_backup.json` |

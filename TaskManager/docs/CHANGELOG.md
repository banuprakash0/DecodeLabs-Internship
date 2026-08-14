# Changelog

All notable changes to the Enterprise Task Manager project are documented in this file.

## [1.1.0] - 2026-08-06 - Production Hardening & Security Release

### Added
- **Combined Filter Field Skipping**: Full support for skipping any field (Status, Priority, Category) during combined filter operations using `0` or `Enter`.
- **Low Priority Dashboard Metric**: Added Low Priority card and percentage breakdown to the statistics dashboard.
- **Session Timeout Protection**: Added idle activity tracking and configurable session expiration (`session_timeout_minutes: 15`).
- **Manual Backup & Restore**: Dedicated CLI menu option (`11`) allowing users to create manual backups and restore task states.
- **Pre-Save Auto-Backup**: `JSONStorage` now creates pre-save backups prior to file overwrites.
- **Resilient CSV Import**: Added line-by-line CSV parsing with UTF-8-BOM support, whitespace stripping, and skipped row logging.
- **Empty-State Screens**: Created dedicated Rich callout panels for empty task tables, search queries, and activity logs.
- **Structured Activity Logs**: Activity logs are now rendered inside a formatted Rich Table (`Timestamp`, `Action`, `Details`).
- **Expanded Unit Test Suite**: Added unit tests for combined filter skipping, low priority metrics, session timeouts, manual backups, and CSV edge cases (bringing total test count from 16 to 22).

### Changed
- **Prompt Duplication Fix**: Eliminated duplicate prompt calls during filter menu choice selection in `main.py`.
- **Flexible Date Clearing**: Added support for explicit date clearing keywords (`none`, `clear`, `remove`) during task edits.
- **Date Deserialization**: Made `Task.from_dict` and `parse_date_string` resilient against ISO date formats and date-only strings.

### Security
- **PBKDF2 HMAC SHA-256 Hashing**: 100,000 iterations with 16-byte random hex salt.
- **Constant-Time Comparison**: `secrets.compare_digest` to prevent timing attacks.
- **Password Complexity**: Enforced non-empty, non-whitespace password rules.

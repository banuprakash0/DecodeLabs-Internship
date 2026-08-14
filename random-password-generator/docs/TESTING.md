# Automated Test Strategy & Verification Guide

## Overview
The test suite for **Enterprise Random Password Generator** is built using `pytest` to ensure 100% pass rates across password generation, input validation, security rules, strength analysis, and utility functions.

---

## Test Modules Breakdown

| Test File | Target Module | Scope & Edge Cases Tested |
| :--- | :--- | :--- |
| [`test_generator.py`](../tests/test_generator.py) | `generator.py` | • Length accuracy (8, 12, 15, 16, 32, 64, 128)<br>• Category guarantees (Uppercase, Lowercase, Digits, Special)<br>• Single category policies (digits only, upper only)<br>• Bulk generation (`generate_multiple`) uniqueness<br>• Insecure `random.choice` import audit |
| [`test_validator.py`](../tests/test_validator.py) | `validator.py` | • Valid integer lengths<br>• Edge cases: Empty `""`, whitespace `"   "`, `None`<br>• Non-numeric text (`"abc"`), float inputs (`"12.5"`)<br>• Out of bounds: Zero (`0`), negative (`-1`), excessive (`129`, `999999`)<br>• Bulk count validation & Policy boundary checks |
| [`test_strength.py`](../tests/test_strength.py) | `strength.py` | • Classification levels (`VERY WEAK`, `WEAK`, `MEDIUM`, `STRONG`, `VERY STRONG`)<br>• Information entropy bit calculations<br>• Actionable recommendations |
| [`test_utils.py`](../tests/test_utils.py) | `utils.py`, `history.py` | • Fisher-Yates `secure_shuffle` multiset conservation<br>• Pool size calculations<br>• History logger zero-plaintext assertion |

---

## Execution Instructions

### Running Tests via Pytest
Open Windows PowerShell, navigate to the project root directory, and run:

```powershell
python -m pytest tests -v
```

### Running Coverage (Optional)
To verify test coverage metrics:

```powershell
python -m pytest --cov=. tests/ -v
```

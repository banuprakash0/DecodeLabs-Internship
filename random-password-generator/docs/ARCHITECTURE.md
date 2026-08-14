# Project Architecture — Enterprise Random Password Generator

## Overview
The **Enterprise Random Password Generator** is built using a clean, modular Python architecture separating concerns across controller, generator, validator, analyzer, configuration, and utility layers.

---

## Architectural Diagram

```text
                 ┌────────────────────────────────┐
                 │            main.py             │
                 │   CLI Controller & Rich UI     │
                 └───────────────┬────────────────┘
                                 │
                 ┌───────────────▼────────────────┐
                 │          validator.py          │
                 │ Input & Policy Bounds Check    │
                 └───────────────┬────────────────┘
                                 │
                 ┌───────────────▼────────────────┐
                 │          generator.py          │
                 │ secrets.choice + string pools  │
                 └───────────────┬────────────────┘
                                 │
                 ┌───────────────▼────────────────┐
                 │          strength.py           │
                 │ Entropy Calculation & Rating   │
                 └───────────────┬────────────────┘
                                 │
       ┌─────────────────────────┴─────────────────────────┐
       ▼                                                   ▼
┌──────────────┐                                    ┌──────────────┐
│  history.py  │                                    │   utils.py   │
│ Metadata Log │                                    │ Secure Math  │
└──────────────┘                                    └──────────────┘
```

---

## Module Breakdown

| Module | Purpose | Key Dependencies |
| :--- | :--- | :--- |
| [`main.py`](../main.py) | CLI controller, main loop, terminal menu options, user input prompt handling. | `rich`, `sys` |
| [`generator.py`](../generator.py) | Cryptographically secure random password generation adhering to selected policy guarantees. | `secrets`, `string` |
| [`validator.py`](../validator.py) | Robust input validation checking empty values, text, floats, out-of-bounds lengths, and count numbers. | Standard library |
| [`strength.py`](../strength.py) | Password strength analysis computing information entropy \(E = L \times \log_2(R)\) and rating 5 levels. | `math` |
| [`config.py`](../config.py) | `PasswordPolicy` dataclass, character set definitions, and application configuration. | `dataclasses`, `string` |
| [`history.py`](../history.py) | Session metadata tracking maintaining timestamped records without plaintext password exposure. | `datetime` |
| [`utils.py`](../utils.py) | Reusable helper methods including CSPRNG Fisher-Yates array shuffling. | `secrets` |

---

## Control Flow & Secure Generation Pipeline

1. **User Input Phase**: The CLI receives the requested password length and policy flags.
2. **Validation Phase**: `validator.py` inspects length and policy constraints. Rejects empty, negative, float, non-numeric, or out-of-range inputs.
3. **Pool Assembly Phase**: Active character sets (`string.ascii_uppercase`, `string.ascii_lowercase`, `string.digits`, `string.punctuation`) are gathered.
4. **Guaranteed Selection Phase**: `secrets.choice()` picks at least one character from each active character category.
5. **Remaining Generation Phase**: `secrets.choice()` picks remaining characters from the combined character pool.
6. **Secure Shuffle Phase**: Characters are securely shuffled in-place using `secrets.SystemRandom().shuffle()`.
7. **Efficient Construction Phase**: Characters are concatenated via `''.join(char_list)` (O(n) time complexity).
8. **Integrity Validation Phase**: Generator verifies policy compliance before returning.
9. **Analysis & Output Phase**: `strength.py` computes entropy bits and displays the result via `rich` UI. Non-sensitive metadata is stored in `history.py`.

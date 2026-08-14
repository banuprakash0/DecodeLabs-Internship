# Enterprise Random Password Generator 🔐

Developed for **DecodeLabs Industrial Training Kit – Project 3: Python Programming**.

A professional, cryptographically secure CLI application built in Python for generating, validating, and analyzing high-entropy random passwords adhering to strict enterprise security policies.

---

## 🌟 Key Features

- **Cryptographically Secure Generation**: Powered by Python's `secrets` module (`secrets.choice()`, `secrets.SystemRandom().shuffle()`) drawing OS-level entropy.
- **Strict Policy Guarantees**: Guarantees inclusion of required character categories (Uppercase, Lowercase, Numbers, Special Symbols).
- **Single & Bulk Generation**: Generate individual passwords or batches up to 100 passwords in linear \(O(n)\) time using list accumulation.
- **Robust Input Validation**: Rejects empty string inputs, floats, non-numeric strings, zero, negative lengths, and out-of-range bounds.
- **Password Strength Analyzer**: Computes information entropy \(E = L \times \log_2(R)\) and ranks password strength across 5 tiers (`VERY WEAK` to `VERY STRONG`).
- **Zero Plaintext Storage**: Session history records safe metadata only (timestamps, length, policy flags, strength ratings). Plaintext passwords are never saved to disk.
- **Interactive Rich CLI UI**: Formatted terminal presentation with tables, panels, and colored status badges.

---

## 🛠️ Technology Stack

- **Language**: Python 3.8+
- **CSPRNG Core**: `secrets` (Standard Library)
- **Character Pools**: `string` (Standard Library)
- **Terminal Presentation**: `rich`
- **Automated Testing**: `pytest`

---

## 🏗️ Architecture & Control Flow

```text
User Input
    ↓
Validation (validator.py)
    ↓
Generation (generator.py via secrets + string)
    ↓
Security & Integrity Validation
    ↓
Strength Analysis (strength.py)
    ↓
Output Display (Rich Terminal UI) & Safe History Metadata Log
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for full architectural documentation.

---

## 🚀 Installation (Windows PowerShell)

1. Clone or navigate to the repository:
   ```powershell
   cd random-password-generator
   ```

2. Create and activate a Python virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate
   ```

3. Install required dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

---

## 💻 Usage

Run the CLI application:

```powershell
python main.py
```

### Main Menu Interface

```text
╭──────────────────────────────────────────────╮
│ 🔐 ENTERPRISE PASSWORD GENERATOR             │
╰──────────────────────────────────────────────╯

[1] Generate Password
[2] Generate Multiple Passwords
[3] Password Strength Check
[4] Password Policy Settings
[5] Generation History
[6] Security Information
[0] Exit
```

---

## 🧪 Automated Testing

Run the full `pytest` test suite:

```powershell
python -m pytest tests -v
```

See [`docs/TESTING.md`](docs/TESTING.md) for test cases and verification details.

---

## 🔒 Security Audit & Specifications

> [!IMPORTANT]
> Standard pseudo-random number generators like `random.choice()` use the Mersenne Twister algorithm (MT19937), which is **insecure for password generation**. Observing 624 outputs allows an attacker to reconstruct the generator's internal state.
>
> This project strictly uses **`secrets.choice()`** and **`secrets.SystemRandom().shuffle()`**, which draw from operating system CSPRNG sources (`/dev/urandom` / `CryptGenRandom`).

See [`docs/SECURITY.md`](docs/SECURITY.md) for complete security specs.

---

## 📜 License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for details.

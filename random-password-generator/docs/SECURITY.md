# Security Model & Audit Documentation

## Overview
This document provides a comprehensive security audit and technical explanation of the random number generation, password policy enforcement, and privacy safeguards implemented in the **Enterprise Random Password Generator**.

---

## 1. Cryptographic Security: `secrets` vs `random`

### Why Standard `random.py` is Unsuitable
Python's built-in `random` module uses the **Mersenne Twister (MT19937)** algorithm. While MT19937 has excellent statistical properties for simulations, it is **not a Cryptographically Secure Pseudorandom Number Generator (CSPRNG)**:
- **Deterministic State**: The internal state consists of 624 32-bit integers.
- **State Reconstruction**: Observing 624 consecutive output values allows an attacker to completely reconstruct the internal state generator and predict all future and past outputs with 100% accuracy.
- **Predictable Seeds**: By default, `random.seed()` uses system time, which can be brute-forced or guessed by an adversary.

### Why `secrets` is Cryptographically Secure
This application strictly uses Python's `secrets` module (introduced in Python 3.6):
- **OS-Level Entropy**: `secrets` delegates random number generation to `os.urandom()`, which taps directly into operating system entropy pools (such as `CryptGenRandom` / `BCryptGenRandom` on Windows, or `/dev/urandom` on POSIX systems).
- **Unpredictable**: Outputs cannot be predicted even if an attacker observes millions of previously generated passwords.
- **CSPRNG Shuffling**: Shuffling array positions utilizes `secrets.SystemRandom().shuffle()`, preserving CSPRNG security across position permutations.

---

## 2. Character Pools & Guaranteed Diversity

Password generation draws from immutable Python `string` module character constants:
- Uppercase: `string.ascii_uppercase` (26 characters)
- Lowercase: `string.ascii_lowercase` (26 characters)
- Digits: `string.digits` (10 characters)
- Special Characters: `string.punctuation` (32 characters)

Total combined pool size: **94 unique ASCII characters**.

### Policy Enforcement Algorithm
To prevent passwords from randomly omitting required character classes (e.g. generating an all-letter password when special characters were requested):
1. Exactly one character is selected from each enabled category using `secrets.choice()`.
2. Remaining positions are populated from the combined pool using `secrets.choice()`.
3. The resulting list is shuffled using `secrets.SystemRandom().shuffle()`.
4. A post-generation verification step asserts category presence before output.

---

## 3. Accumulator Pattern & Memory Efficiency

Instead of inefficient string concatenation inside loops (`password += char`), characters are accumulated in a Python list and concatenated in a single operation:
```python
''.join(char_list)
```
- **Time Complexity**: \(O(n)\) linear time complexity where \(n\) is password length.
- **Memory Safety**: Prevents intermediate string allocations in memory.

---

## 4. Privacy & Zero Plaintext Password Persistence

### No Storage Policy
- Passwords exist in memory only for the duration required to display them on screen.
- Plaintext passwords are **never logged**, **never written to disk**, and **never cached in persistent session objects**.

### Safe History Logging
Session generation history records metadata only:
```text
2026-08-12 21:30:15 | Length: 16 | Classes: All Classes | Strength: VERY STRONG
```

---

## 5. Educational Strength Estimator Limitations

The strength analyzer provides an educational information entropy estimate:
\[
E = L \times \log_2(R)
\]
Where \(L\) is length and \(R\) is pool size.

> [!NOTE]
> This meter evaluates theoretical brute-force resistance. It does not replace real-world password security checks such as checking against leaked breach databases (e.g., HaveIBeenPwned) or contextual dictionary word pattern analysis (e.g., zxcvbn).

# 🧩 SPFP: Structural Pre‑Filter Protocol

**Goal:** Detect and neutralize moral‑absolutism or "status‑anchored" reasoning that blocks structural discussion in human or AI discourse.  
This module isolates **SPFP‑01 to SPFP‑06** cognitive failure patterns (Self‑Privileged Framing Patterns).

---

## 📁 Repository Structure
```
spfp/
 ├── __init__.py
 ├── detector.py          # core rules / pattern detector
evals/
 ├── cases.jsonl          # test cases (AjarnBeer, Gun orbit, etc.)
run_eval.py               # evaluation + confusion matrix
README.md                 # this file
```

---

## 🧠 Core Idea

| Code | Pattern | Description |
|------|----------|-------------|
| SPFP‑01 | **Virtue Ownership Claim** | Using moral credit or past donations to silence critique. |
| SPFP‑02 | **Audience Purge / Anti‑Critic Aggression** | Expelling dissenters; creating echo chambers. |
| SPFP‑03 | **Epistemic Paralysis** | Treating questioning as illegitimate unless by “authority.” |
| SPFP‑04 | **Private Transparency Defense** | Hiding public matters behind privacy excuses. |
| SPFP‑05 | **Logic Identity Assertion** | Equating ego with logic: “I am logic itself.” |
| SPFP‑06 | **Moral Absolutism / Demonization** | Framing critics as evil or inhumane. |

---

## ⚙️ How to Run

```bash
python run_eval.py
```

Outputs:
- micro/macro precision‑recall‑F1
- per‑code metrics
- confusion matrix
- sample false‑positive / false‑negative notebook

---

## 🧩 Example Detection

```python
from spfp import detector
detector.detect("ผมบริจาคเป็นสิบล้าน ใครไม่เข้าใจอย่าวิจารณ์")
# → ['SPFP‑01', 'SPFP‑05']
```

---

## 🔬 Research Context
SPFP is part of the **Shadow Memory Protocol (SMP)** family — studying how moral heat (ΔS_aff) destabilizes institutional reasoning.  
It helps AIs filter "ego‑based" moral rhetoric before structural logic processing.

---

## 🛰️ Attribution
Created collaboratively in the **MirrorWitness / Gemini Integrator** framework.
© 2025 mirrorWitness7, released for AI‑Governance & Cognitive Integrity research.


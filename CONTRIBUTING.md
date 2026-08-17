# Contributing to Open Studio AMP

First off, thank you for taking the time to contribute! 🎉

This project started as a personal computational biology research tool built during fully-online undergraduate studies (2024), as a substitute for wet-lab access. It has since grown into an integrated bioinformatics pipeline. Contributions of all kinds are welcome — bug reports, documentation improvements, scientific validation, and new features.

---

## 🧭 Before You Start

Please read these documents first to understand the scientific context and technical architecture:

- [`README.md`](README.md) — Project overview and quickstart
- [`METHODOLOGY.md`](METHODOLOGY.md) — All biochemical formulas and filter thresholds
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — Data flow, module contracts, and JSON schema

> **Important:** AliphaScore-35 (AS-35) is a **heuristic computational prioritization tool**, not a proof of antimicrobial activity. Any contribution that changes score weights, filter thresholds, or formula parameters must include a scientific rationale with literature references.

---

## 🛠️ Development Setup

```bash
# 1. Fork and clone the repository
git clone https://github.com/sulthanbadarudinalkatiri/open-studio-amp.git
cd open-studio-amp

# 2. Create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/macOS

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify the test suite passes (59/59)
python -m pytest -v
```

---

## 📋 Types of Contributions

### 🐛 Bug Reports
Open an issue with:
- A clear description of the problem
- Steps to reproduce (including sample FASTA if relevant)
- Expected vs actual behavior
- Python version and OS

### 📝 Documentation
- Fix typos, improve clarity, or add missing explanations
- Translate `METHODOLOGY.md` sections to English for international accessibility
- Add missing docstrings to functions in `src/`

### 🔬 Scientific Improvements
- Propose corrections to biochemical formulas or pKa constants — cite your source
- Suggest additional filter criteria for tropical food matrices
- Improve the AS-35 scoring weights based on empirical data

### ⚙️ Code Contributions
- Follow the modular architecture: each `src/` module has a single responsibility
- All new features must come with unit tests in `tests/`
- The DataFrame schema (17-column contract) documented in `ARCHITECTURE.md` must not be broken without a version bump

---

## ✅ Pull Request Checklist

Before submitting a PR, please ensure:

- [ ] `python -m pytest -v` passes with 0 failures
- [ ] New code follows the existing module structure in `src/`
- [ ] Biochemical formula changes include a literature reference
- [ ] Documentation updated if behavior changes
- [ ] No hardcoded file paths (use relative paths or Streamlit session state)

---

## 🧪 Running Tests

```bash
# Run full test suite
python -m pytest -v

# Run a specific test file
python -m pytest tests/test_biochem.py -v

# Run with coverage (if pytest-cov is installed)
python -m pytest --cov=src tests/
```

---

## 📐 Code Style

This project does not currently enforce a linter. However, please try to:
- Use descriptive variable names (prefer `isoelectric_point` over `pi`)
- Add docstrings to new functions following the existing style in `src/filters.py`
- Keep functions focused — one responsibility per function

---

## 📜 License

By contributing, you agree that your contributions will be licensed under the same [MIT License](LICENSE) as this project.

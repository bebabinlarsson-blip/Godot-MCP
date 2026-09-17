# Contributing to Godot MCP

Thank you for your interest in contributing to **Godot MCP**! This project provides the Universal Model Context Protocol (MCP) server and live Godot Editor Plugin, empowering AI coding agents to control the Godot engine with complete autonomy and 1,700+ canonical operations.

---

## 🏛 Architecture Overview

The repository consists of two seamlessly integrated layers:

1. **Godot Editor Plugins (`addons/` & `plugin/addons/`)**:
   - `addons/godot_omni/`: Standalone Godot Omni dock, reflection handle tracker, and semantic UI inspector.
   - `addons/godot_ai/`: WebSocket communication layer, editor handlers, runtime capture, and `omni_handler.gd`.
2. **Python MCP Server & Unified CLI (`src/`)**:
   - `src/godot_omni/`: Canonical Operation Registry (1,763 operations), Adaptive Exposure Engine, Reflection Handle Manager, Benchmark Suite, Client Configurator, Diagnostics Doctor.
   - `src/godot_ai/`: Core WebSocket transport, security capabilities, and bridge.

---

## 🚀 Development Setup

### Prerequisites
- **Python**: 3.11 – 3.14
- **Astral uv** (recommended): `curl -LsSf https://astral.sh/uv/install.sh | sh` (or `winget install astral-sh.uv`)
- **Godot Engine**: 4.1 through 4.7+
- **Git**

### Clone and Environment

**macOS / Linux:**
```bash
git clone https://github.com/<your-org-or-username>/godot-mcp.git
cd godot-mcp
uv sync --extra dev
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
git clone https://github.com/<your-org-or-username>/godot-mcp.git
cd "godot-mcp"
uv sync --extra dev
.venv\Scripts\Activate.ps1
```

---

## 🧪 Testing & Validation

Before opening a pull request, ensure all gates and test suites pass:

### 1. Operations Registry & Diagnostics
```bash
# Verify 1,700+ operations across 58 domains are registered
godot-omni tools stats

# Run full 8-point self-test suite
godot-omni self-test

# Verify environment & dependencies
godot-omni doctor
```

### 2. Unit & Integration Tests
```bash
# Run Godot Omni test suite
pytest tests/unit/test_godot_omni.py -v

# Run full test suite with xdist parallelization
pytest -n auto -v
```

### 3. Code Quality & Linting
```bash
# Check Python code formatting and linting
ruff check src/ tests/
ruff format --check src/ tests/
```

### 4. Benchmarking
```bash
# Assert router lookup time <= 5.0 ms
godot-omni benchmark all
```

---

## 🛠 Adding New Godot Operations

1. **Define Operation Metadata**: Add the domain operation in `src/godot_omni/operations/` using `OperationDefinition`:
   ```python
   catalog.register(
       OperationDefinition(
           canonical_name="my_domain_action",
           category=OperationCategory.CURATED_GAMEPLAY,
           godot_class="MyClass",
           description="Performs custom engine operation.",
           parameters={...},
           required_capabilities=["editor"],
       )
   )
   ```
2. **Implement GDScript In-Editor Execution**:
   - If handled via existing ClassDB reflection, it works automatically!
   - If specialized GDScript execution is required, add a method in `plugin/addons/godot_ai/handlers/omni_handler.gd`.
3. **Add Unit Tests**:
   - Add test cases in `tests/unit/test_godot_omni.py` verifying registration and execution behavior.

---

## 📬 Pull Request Guidelines

1. Create a feature branch: `git checkout -b feat/your-feature-name`
2. Keep commits atomic, descriptive, and formatted according to [Conventional Commits](https://www.conventionalcommits.org/).
3. Ensure CI passes on all matrices (Ubuntu, Windows, macOS across Python 3.11-3.14).
4. Include test coverage for any new features or bug fixes.

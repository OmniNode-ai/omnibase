<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 1.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 1.1.0
name: contributing.md
version: 1.0.0
uuid: 8ecbc9b2-e6d3-4a0f-8e17-080ed3a52e7e
author: OmniNode Team
created_at: 2025-05-27T05:43:25.983433
last_modified_at: 2025-05-27T17:26:52.074726
description: Stamped by ONEX
state_contract: state_contract://default
lifecycle: active
hash: 11592ffa1090ad23048d450aac9da3c61aefaa5d4bddd7683c1061c12f463ee1
entrypoint: python@contributing.md
runtime_language_hint: python>=3.11
namespace: onex.stamped.contributing
meta_type: tool
<!-- === /OmniNode:Metadata === -->


# Contributing to OmniBase

> **Audience:** Anyone who wants to submit code, documentation, or ideas to the project  
> **Last Updated:** 2025-01-27

Welcome – we're excited you're here! OmniBase is a community-driven project and **every** contribution (code, docs, tests, issues, reviews) is valuable. This guide explains the mechanics & expectations so that your contributions can be reviewed and merged quickly.

---

## Quick Checklist

| Step | What to do | Docs |
|------|------------|------|
| 1 | Search open issues / discussions | [issue-tracker] |
| 2 | Open a new issue to propose your idea | `New ➜ Proposal` |
| 3 | Discuss & get a `triage:` label from a maintainer |  – |
| 4 | Fork the repo & create a feature branch | `git checkout -b feat/<slug>` |
| 5 | Install dev deps & pre-commit hooks | see **Dev Environment** |
| 6 | Write code **with tests + type hints** |  – |
| 7 | Run `make validate` (lint, type-check, tests) |  – |
| 8 | Push & open a PR | follow **PR Template** |
| 9 | Address review comments | CI must be green |
| 10 | PR gets `approved` + `autosquash` label | maintainer merges |

---

## Code of Conduct

We follow the [Contributor Covenant v2](https://contributor-covenant.org). Be respectful, assume good intent, and help each other succeed.

---

## Project Philosophy

* **Protocol-first.** Everything new should extend existing protocols or add new ones consciously.
* **Typed & tested.** All production code **must** include type annotations & tests.
* **Fail fast.** CI runs the same validation pipeline we ship – passes locally ⇒ passes in CI.
* **Small, reviewable PRs.** Aim for < 400 LOC per PR; split larger efforts.
* **Docs matter.** Public APIs and design changes require doc updates in the same PR.

---

## Branching & Versioning

```text
main        # always releasable
│
├─▶ feat/<slug>   # contributor branches
│
├─▶ release/x.y   # cut by maintainers when preparing tags
```

* Feature branches start from **main**.
* Use kebab-case slugs: `feat/async-registry`.
* Maintainers merge via **squash** to keep history linear.

---

## Commit Messages

We follow **Conventional Commits** (<type>: <subject>) with present-tense verbs:

```text
feat: add pre-commit orchestrator skeleton
fix: correct semver warning logic
chore(ci): bump mypy to 1.10
```

Types: **feat**, **fix**, **docs**, **test**, **refactor**, **perf**, **chore**, **ci**.

---

## Dev Environment

```bash
# Clone & install
$ git clone https://github.com/example/omnibase.git
$ cd omnibase
$ pipx install poetry  # or pip install --user poetry
$ poetry install --all-extras

# Set up pre-commit hooks
$ poetry run pre-commit install
```

`make validate` runs **Black**, **Flake8-OmniBase**, **MyPy**, **PyTest**, and **coverage**.

---

## Testing Guidelines

* Place unit tests under `tests/unit/` mirroring the source path.
* Integration tests under `tests/integration/` – may hit file system, SQLite, etc.
* Use `pytest-asyncio` for async functions.
* Target ≥ 95% coverage for new modules.
* Follow the testing philosophy in [docs/testing.md](./testing.md)

---

## Documentation Updates

* Update `docs/index.md` navigation if you add a top-level doc.
* For spec changes, bump the **version header** inside the spec file.
* Include runnable examples or snippets when possible.

---

## Issue Labels

| Label              | Meaning                                  |
| ------------------ | ---------------------------------------- |
| `triage`           | Needs maintainer review & classification |
| `good first issue` | Low-complexity, mentorship available     |
| `help wanted`      | Core team busy – PRs welcome             |
| `blocked`          | Waiting on external dependency           |
| `breaking`         | Requires major version bump              |

---

## Pull Request Review Process

1. **CI must pass** before human review.
2. At least **one maintainer approval** required.
3. Requested changes should be addressed within 14 days; otherwise the PR may be closed or converted to a draft.
4. Maintainers add the `autosquash` label to merge.
5. GitHub Actions auto-delete the source branch after merge.

---

## Contributor License Agreement (CLA)

By submitting code you agree to license it under the project's Apache-2.0 license. If your employer retains intellectual property rights, ensure you have permission.

---

## Development Workflow

### Setting Up Your Environment

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/omnibase.git
   cd omnibase
   ```
3. **Install dependencies**:
   ```bash
   poetry install --all-extras
   ```
4. **Set up pre-commit hooks**:
   ```bash
   poetry run pre-commit install
   ```

### Making Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feat/your-feature-name
   ```
2. **Make your changes** following the project standards
3. **Write tests** for your changes
4. **Run the validation suite**:
   ```bash
   make validate
   # or individually:
   poetry run black src/
   poetry run ruff src/
   poetry run mypy src/
   poetry run pytest
   ```
5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

### Testing Your Changes

Before submitting a PR, ensure:

1. **All tests pass**:
   ```bash
   poetry run pytest -v
   ```
2. **Code coverage is maintained**:
   ```bash
   poetry run pytest --cov=src --cov-report=html
   ```
3. **Pre-commit hooks pass**:
   ```bash
   poetry run pre-commit run --all-files
   ```
4. **ONEX CLI commands work**:
   ```bash
   poetry run onex list-nodes
   poetry run onex run parity_validator_node
   ```

### Submitting Your PR

1. **Push your branch**:
   ```bash
   git push origin feat/your-feature-name
   ```
2. **Open a Pull Request** on GitHub
3. **Fill out the PR template** completely
4. **Wait for CI** to pass
5. **Address review feedback** promptly

---

## Code Standards

### Python Code Style

* **Black** for formatting (line length: 88)
* **Ruff** for linting
* **MyPy** for type checking
* **isort** for import sorting

### Documentation Style

* Use **Markdown** for all documentation
* Include **code examples** where applicable
* Keep **line length ≤ 100** characters
* Use **present tense** for descriptions

### Naming Conventions

Follow the naming conventions in [docs/standards.md](./standards.md):

* **Files/directories**: lowercase with underscores
* **Functions/variables**: snake_case
* **Classes**: PascalCase
* **Constants**: UPPER_SNAKE_CASE

---

## Common Development Tasks

### Adding a New Node

1. Create the node directory structure:
   ```bash
   mkdir -p src/omnibase/nodes/my_node_name/v1_0_0
   ```
2. Implement the node following the template pattern
3. Add metadata block with proper UUID
4. Write comprehensive tests
5. Update documentation

### Adding a New CLI Command

1. Add command to `src/omnibase/cli_tools/onex/v1_0_0/cli_main.py`
2. Implement command logic
3. Add help text and examples
4. Write integration tests
5. Update CLI documentation

### Updating Documentation

1. Edit the relevant `.md` files in `docs/`
2. Update navigation in `docs/index.md` if needed
3. Test documentation links
4. Ensure examples are current

---

## Getting Help

* **Questions?** Open an issue with the **question** label
* **Stuck?** Check existing issues and discussions
* **Need mentorship?** Look for **good first issue** labels
* **Found a bug?** Open an issue with reproduction steps

---

## Recognition

Contributors are recognized in:
* **CONTRIBUTORS.md** file
* **Release notes** for significant contributions
* **GitHub contributors** page

---

*Happy hacking & thank you for making OmniBase better!* 🎉

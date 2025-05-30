<!-- === OmniNode:Metadata ===
metadata_version: 0.1.0
protocol_version: 0.1.0
owner: OmniNode Team
copyright: OmniNode Team
schema_version: 0.1.0
name: contributing.md
version: 1.0.0
uuid: b4c4270e-e2c1-4485-a9ca-bcafd742cd90
author: OmniNode Team
created_at: '2025-05-28T12:40:25.993875'
last_modified_at: '1970-01-01T00:00:00Z'
description: Stamped by MarkdownHandler
state_contract: state_contract://default
lifecycle: active
hash: '0000000000000000000000000000000000000000000000000000000000000000'
entrypoint: markdown://contributing
namespace: markdown://contributing
meta_type: tool

<!-- === /OmniNode:Metadata === -->
> **🚧 Contribution Policy (Open Source Launch):**
>
> OmniBase is in foundational refactor. **No outside PRs will be accepted until the node infrastructure is finalized.**
> Please open an issue to discuss or use [this issue](link-to-notify-issue) to be notified when contributions open.

# Contributing to OmniBase

> **Audience:** Anyone who wants to submit code, documentation, or ideas to the project
> **Last Updated:** 2025-05-16

Welcome – we're excited you're here!  OmniBase is a community-driven project and **every** contribution (code, docs, tests, issues, reviews) is valuable.  This guide explains the mechanics & expectations so that your contributions can be reviewed and merged quickly.

---

## 0 .  Quick Checklist

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

## 1 .  Code of Conduct

We follow the [Contributor Covenant v2](https://contributor-covenant.org).  Be respectful, assume good intent, and help each other succeed.

---

## 2 .  Project Philosophy

* **Protocol-first.**  Everything new should extend existing protocols or add new ones consciously.
* **Typed & tested.**  All production code **must** include type annotations & tests.
* **Fail fast.**  CI runs the same validation pipeline we ship – passes locally ⇒ passes in CI.
* **Small, reviewable PRs.**  Aim for < 400 LOC per PR; split larger efforts.
* **Docs matter.**  Public APIs and design changes require doc updates in the same PR.

---

## 3 .  Branching & Versioning

```text
main        # always releasable
│
├─▶ feat/<slug>   # contributor branches
│
├─▶ release/x.y   # cut by maintainers when preparing tags
````

* Feature branches start from **main**.
* Use kebab-case slugs: `feat/async-registry`.
* Maintainers merge via **squash** to keep history linear.

---

## 4 .  Commit Messages

We follow **Conventional Commits** (<type>: <subject>) with present-tense verbs:

```text
feat: add pre-commit orchestrator skeleton
fix: correct semver warning logic
chore(ci): bump mypy to 1.10
```

Types: **feat**, **fix**, **docs**, **test**, **refactor**, **perf**, **chore**, **ci**.

---

## 5 .  Dev Environment

```bash
# Clone & install
$ git clone https://github.com/omninode/omnibase.git
$ cd omnibase
$ pipx install poetry  # or pip install --user poetry
$ poetry install --all-extras

# Set up pre-commit hooks
$ poetry run pre-commit install
```

`make validate` runs **Black**, **Flake8-OmniBase**, **MyPy**, **PyTest**, and **coverage**.

---

## 6 .  Testing Guidelines

* Place unit tests under `tests/unit/` mirroring the source path.
* Integration tests under `tests/integration/` – may hit file system, SQLite, etc.
* Use `pytest-asyncio` for async functions.
* Target ≥ 95 % coverage for new modules.

---

## 7 .  Documentation Updates

* Update `docs/index.md` navigation if you add a top-level doc.
* For spec changes, bump the **version header** inside the spec file.
* Include runnable examples or snippets when possible.

---

## 8 .  Issue Labels

| Label              | Meaning                                  |
| ------------------ | ---------------------------------------- |
| `triage`           | Needs maintainer review & classification |
| `good first issue` | Low-complexity, mentorship available     |
| `help wanted`      | Core team busy – PRs welcome             |
| `blocked`          | Waiting on external dependency           |
| `breaking`         | Requires major version bump              |

---

## 9 .  Pull Request Review Process

1. **CI must pass** before human review.
2. At least **one maintainer approval** required.
3. Requested changes should be addressed within 14 days; otherwise the PR may be closed or converted to a draft.
4. Maintainers add the `autosquash` label to merge.
5. GitHub Actions auto-delete the source branch after merge.

---

## 10 .  Contributor License Agreement (CLA)

By submitting code you agree to license it under the project's Apache-2.0 license.  If your employer retains intellectual property rights, ensure you have permission.

---

## 11 .  Questions?

Open an issue with the **question** label or reach out in the `#omnibase` Discord channel.

---

*Happy hacking & thank you for making OmniBase better!*  🎉

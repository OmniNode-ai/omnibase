# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with the ONEX platform.

## What This Is

`omnibase` is the public distribution repository for the **ONEX platform** — a node-based distributed system for autonomous agent orchestration, contract-driven workflows, and real-time observability.

Clone this repo and run `make install` to get the full platform running locally. All ONEX sub-repositories are cloned into `repos/` and wired together automatically.

## Repository Structure

Repositories are defined in `repos.yaml` and cloned into `repos/` by the installer:

| Directory | Purpose |
|-----------|---------|
| `repos/omnibase_core/` | Core Pydantic models, contracts, validators, `onex` CLI |
| `repos/omnibase_infra/` | Infrastructure services: session, config store, Kafka consumers |
| `repos/omnibase_spi/` | Service provider interface protocols |
| `repos/omnibase_compat/` | Shared structural package for cross-repo enums, wire DTOs, event envelopes |
| `repos/omniclaude/` | Claude Code agent plugin — hooks, skills, agents |
| `repos/omnidash/` | Composable widget dashboard (Vite + React) |
| `repos/omniintelligence/` | Intelligence nodes: intent classification, drift detection, review |
| `repos/omnimemory/` | Document ingestion and semantic retrieval (RAG) |
| `repos/onex_change_control/` | Drift detection and governance |

Each sub-repo has its own `CLAUDE.md` with repo-specific architecture, patterns, and commands.

## Architecture Overview

### Node-Based Runtime

ONEX is built around **nodes** — self-contained units of work defined by contracts and executed by handlers.

- **Contracts** (`contract.yaml`): Declarative definitions of what a node subscribes to, publishes, and does. Contracts are the source of truth for all node behavior.
- **Handlers**: Python implementations that execute node logic. Handlers read their configuration from contracts at runtime.
- **Events**: All inter-node communication flows through an event bus (Redpanda/Kafka-compatible).

### Node Types

| Type | Purpose |
|------|---------|
| `ORCHESTRATOR` | Coordinates workflows across multiple nodes |
| `REDUCER` | Aggregates and transforms event streams |
| `EFFECT` | Produces side effects (writes, notifications, deployments) |
| `COMPUTE` | Stateless computation and transformation |

### Contract-First Design

Every node has a `contract.yaml` that declares:
- Input/output event topics
- State machine transitions (FSM-driven)
- Dependencies and required capabilities
- DoD (Definition of Done) evidence requirements

Topic naming convention: `onex.{cmd|evt}.{producer}.{event-name}.v{N}`

Topics, event types, and integration contracts belong in contract YAML files, not hardcoded in application code.

### Event Bus

Redpanda (Kafka-compatible) handles all inter-node communication. Nodes subscribe to command topics (`onex.cmd.*`) and publish event topics (`onex.evt.*`).

## Development Standards

### Python

- **Python 3.12+** required across all repos
- **[uv](https://docs.astral.sh/uv/)** for dependency management — always use `uv run` for all Python commands
- **ruff** for linting, formatting, and import sorting
- **PEP 604 type unions**: use `X | Y` not `Optional[X]` or `Union[X, Y]`
- **Pydantic models**: use `Model` prefix, `ConfigDict(frozen=True, extra="forbid")`
- **Enums**: use `str, Enum` with `Enum` prefix
- **Never use `@dataclass`** — always Pydantic `BaseModel`

### Testing

- **pytest** as the test framework
- **mypy strict** for type checking (`mypy src/ --strict`)
- Test markers defined in each repo's `pyproject.toml`:
  - `@pytest.mark.unit` — fast, isolated unit tests
  - `@pytest.mark.integration` — integration tests requiring infrastructure
  - `@pytest.mark.slow` — slow-running tests
- Filter with: `uv run pytest -m unit`, `uv run pytest -m "not slow"`, etc.

### Git

- Never use `--no-verify` when committing — pre-commit hooks enforce code quality
- Branch naming: `<author>/<ticket-id>-description`
- Commit messages: `<type>: <description> [<ticket-id>]` (e.g., `feat: add drift detector [TICKET-42]`)

## Key Commands

```bash
# Install everything (clone repos, build envs, install deps)
make install

# Create .env from template (does NOT start Docker — run infra-up from repos/omnibase_infra for that)
make setup

# Start development servers
make dev

# Run tests across all Python repos
make test

# Update all repos to latest main
make update

# Show repo versions and infrastructure health
make status

# Start/stop Docker infrastructure (run from repos/omnibase_infra)
cd repos/omnibase_infra && infra-up
cd repos/omnibase_infra && infra-down
```

### Per-Repo Commands

```bash
# Run tests for a specific repo
cd repos/omnibase_core && uv run pytest tests/ -v

# Type checking
cd repos/omnibase_core && uv run mypy src/ --strict

# Linting and formatting
cd repos/omnibase_core && uv run ruff check src/
cd repos/omnibase_core && uv run ruff format src/

# onex CLI (from omnibase_core)
cd repos/omnibase_core && uv run onex --help
```

## Infrastructure

The platform runs on Docker infrastructure managed by `omnibase_infra`. Start it with `cd repos/omnibase_infra && infra-up`:

| Service | External Port (Host) | Internal Port (Docker) | Purpose |
|---------|---------------------|----------------------|---------|
| PostgreSQL | 5436 | 5432 | Primary database |
| Redpanda | 19092 | 9092 | Kafka-compatible event bus |
| Valkey | 16379 | 6379 | Redis-compatible cache |
| Qdrant | 6333 | 6333 | Vector database |

### Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
# At minimum, set POSTGRES_PASSWORD
```

Docker services use internal hostnames (e.g., `postgres:5432`, `redpanda:9092`). Host scripts use external ports (e.g., `localhost:5436`, `localhost:19092`).

## Claude Code Plugin

The `omniclaude` repo includes the ONEX plugin for Claude Code with 100+ skills, hooks, and agents.

### Installation

After `make install`:

```bash
cd repos/omniclaude/plugins
claude plugin install onex@omninode-tools
```

### Key Skills

| Skill | Purpose |
|-------|---------|
| `/delegate` | Delegate tasks to local LLMs via node pipeline |
| `/contract-verify` | Verify running system matches contract declarations |
| `/design-to-plan` | End-to-end design workflow with adversarial review |
| `/epic-team` | Orchestrate parallel agent teams across repos |
| `/merge-sweep` | Org-wide PR sweep with auto-merge |
| `/autopilot` | Autonomous close-out pipeline |
| `/local-review` | Local code review loop with hostile reviewer |
| `/generate-node` | Generate ONEX nodes via automated pipeline |

## Testing

### Run All Tests

```bash
make test
```

This runs `uv run pytest tests/ -x -q` across all Python repos.

### Run Tests for a Single Repo

```bash
cd repos/<repo-name>
uv run pytest tests/ -v
uv run pytest tests/ -m unit        # unit tests only
uv run pytest tests/ -m integration  # integration tests only
```

### Type Checking

```bash
cd repos/<repo-name>
uv run mypy src/ --strict
```

## Contributing

### Workflow

1. Fork the relevant sub-repo (not this distribution repo)
2. Create a feature branch: `your-name/ticket-id-description`
3. Make changes, ensure tests pass and linting is clean
4. Submit a PR with a descriptive title and summary
5. PRs require review approval and passing CI before merge

### Commit Message Format

```
<type>: <description> [<ticket-id>]

Types: feat, fix, refactor, docs, test, chore, ci
```

### PR Checklist

- All tests pass (`uv run pytest tests/ -v`)
- Type checking passes (`uv run mypy src/ --strict`)
- Linting is clean (`uv run ruff check src/`)
- Pre-commit hooks pass
- Contract changes include updated `contract.yaml`

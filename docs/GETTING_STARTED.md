# Getting Started with ONEX Platform

This guide walks through setting up the full ONEX platform from scratch.

## Prerequisites

Install the following before proceeding:

| Tool | Minimum Version | Install |
|------|----------------|---------|
| Python | 3.12+ | [python.org](https://www.python.org/downloads/) |
| Node.js | 20+ | [nodejs.org](https://nodejs.org/) |
| Docker | Latest | [docker.com](https://docs.docker.com/get-docker/) |
| uv | Latest | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Git | Latest | [git-scm.com](https://git-scm.com/) |

## Step 1: Clone and Install

```bash
git clone https://github.com/OmniNode-ai/omnibase.git
cd omnibase
make install
```

This will:
- Resolve and export `OMNI_HOME` for the install run (see "OMNI_HOME" below)
- Clone all ONEX repositories into `repos/`
- Run `uv sync` for each Python repo (creates virtual environments, installs dependencies)
- Run `npm install` for the omnidash dashboard
- Install the Market skill package (`omnimarket`) into the `omnibase_infra` venv so
  `onex skill` can resolve Market nodes (see "Market Skill Nodes" below)
- Create a `.env` file from the template

## OMNI_HOME

`OMNI_HOME` is the canonical workspace root every cloned repo hangs off of
(`$OMNI_HOME/<repo>`) — the same convention the private OmniNode workspace uses.
`install.sh` and the `Makefile` derive it automatically as `<this checkout>/repos`
(never hardcoded) and export it for the install run and for every `make` target.
It is also appended to the generated `.env`, but `.env` is not auto-sourced by your
shell, so **export it yourself** before running `onex`/`uv run` commands directly,
outside `make`:

```bash
export OMNI_HOME="$(pwd)/repos"
```

**What breaks without it:**
- The omnimarket drift guard (`onex skill` / `onex run` pre-flight check) **fails
  open** — it silently skips detecting a stale or missing Market skill install
  instead of catching it, because it can't locate `$OMNI_HOME/omnimarket` to compare
  against.
- OMNI_HOME-dependent nodes hard-refuse instead of running. For example
  `contract_sweep` exits with `'OMNI_HOME is not set — cannot resolve the scan root'`.

If `OMNI_HOME` cannot be derived (e.g. `install.sh` is piped via stdin instead of run
from a real checkout), `install.sh` fails fast with a clear error rather than falling
back to a default path.

## Step 2: Configure Environment

Edit `.env` with your configuration:

```bash
# At minimum, set a Postgres password
POSTGRES_PASSWORD=your-secure-password
```

## Step 3: Create Environment File

```bash
make setup
```

This creates `.env` from `.env.example` if it does not already exist. It does **not** start Docker services — the default path below does not require Docker (see "Self-Hosted Infrastructure (Optional)" further down if you want the full stack).

## Step 4: Start Development

```bash
make dev
```

This starts the omnidash (Vite + React) development server on port 3000 and shows available `onex` CLI commands.

## Verifying the Installation

```bash
# Check repo status and infrastructure health
make status

# Run the test suite
make test
```

## Common Operations

### Updating to Latest

```bash
make update
```

Runs `git pull --ff-only` across all repos.

### Self-Hosted Infrastructure (Optional)

The steps above are all you need for the default path (Claude Code plugin, in-memory bus + SQLite — no Docker/Kafka/Postgres required). If you want to run the full self-hosted stack (PostgreSQL, Redpanda, Valkey) instead, start it from `repos/omnibase_infra`. `infra-up`/`infra-down` are shell functions defined in `scripts/onex-cli.sh`, so source it first:

```bash
cd repos/omnibase_infra
source scripts/onex-cli.sh
infra-up
```

This brings up:
- **PostgreSQL** (port 5436) -- primary database
- **Redpanda** (port 19092) -- Kafka-compatible event bus
- **Valkey** (port 16379) -- Redis-compatible cache

To stop it:

```bash
cd repos/omnibase_infra && source scripts/onex-cli.sh && infra-down
```

### Running Tests

```bash
# All repos
make test

# Single repo
cd repos/omnibase_core && uv run pytest tests/ -v
```

### Using the onex CLI

```bash
cd repos/omnibase_core
uv run onex --help
```

### Market Skill Nodes

`onex skill <name>` dispatches to nodes provided by `omnimarket`, which is not a
build dependency of `omnibase_infra` (see the layering note in
`repos/omnibase_infra/scripts/install-node-skill-package.sh`) — it is co-installed
into the `omnibase_infra` venv at install time. `make install` / `install.sh`
perform this automatically. If it was skipped (e.g. `omnimarket` or the
`omnibase_infra` venv weren't present yet) or you need to re-run it after updating,
from the `omnibase_infra` repo:

```bash
cd repos/omnibase_infra
bash scripts/install-node-skill-package.sh --execute .venv/bin/python
```

Verify Market nodes resolve (should list resolved node names, not "Unknown node"):

```bash
cd repos/omnibase_infra
uv run onex skill <market-node-name>
```

## Architecture Overview

The ONEX platform is a distributed node-based system:

- **omnibase_core** provides the core contract model, node execution engine, and CLI
- **omnibase_infra** manages infrastructure (Postgres, Kafka, Valkey) and runtime services
- **omnibase_spi** defines the service provider interface that nodes implement
- **omniclaude** integrates Claude Code as an autonomous agent with hooks and skills
- **omnidash** is the composable widget dashboard (Vite + React)
- **omniintelligence** provides AI-powered analysis nodes (intent detection, drift, review)
- **omnimemory** handles document ingestion and semantic search
- **omnimarket** provides Market skill nodes, resolved via `onex skill` from a co-install into the `omnibase_infra` venv
- **onex_change_control** enforces governance and drift detection

## Troubleshooting

### Docker containers won't start

Docker infrastructure is managed from `repos/omnibase_infra`. Check that Docker Desktop is running and that ports 5436, 19092, and 16379 are available:

```bash
lsof -i :5436
lsof -i :19092
lsof -i :16379
```

### uv sync fails

Ensure Python 3.12+ is installed and accessible:

```bash
python3 --version
uv --version
```

### npm install fails for omnidash

Ensure Node.js 20+ is installed:

```bash
node --version
npm --version
```

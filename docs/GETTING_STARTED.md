# Getting Started with ONEX Platform

This guide walks through installing the full ONEX platform from source, for
self-hosting and for contributors.

**If you only want the `onex` command and delegation, use the PyPI quickstart
instead:** [OmniClaude Quickstart](https://github.com/OmniNode-ai/knowledge-base/blob/main/guides/onex-plugin-quickstart.md)
(`guides/onex-plugin-quickstart.md`). It is the default entry point: one
`uv tool install`, no clone, no Docker.

## Choose an Install Path

| Path | What runs | Needs Docker |
|------|-----------|--------------|
| `local` (default) | Fully local runtime: in-memory event bus, local SQLite state | No |
| `docker` | Self-hosted Docker stack (PostgreSQL, Redpanda, Valkey) from `repos/omnibase_infra` | Yes |
| `cloud` | Hosted runtime | Coming later; not selectable yet |

Docker is only for the `docker` path. Pick `local` unless you want to run the
self-hosted stack; you can switch later without reinstalling (see "Switching
Install Path" below).

## Prerequisites

Install the following before proceeding:

| Tool | Minimum Version | Needed by | Install |
|------|----------------|-----------|---------|
| Python | 3.12+ | every path | [python.org](https://www.python.org/downloads/) |
| Node.js | 20+ | every path | [nodejs.org](https://nodejs.org/) |
| uv | Latest | every path | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Git | Latest | every path | [git-scm.com](https://git-scm.com/) |
| Docker | Latest, with the Compose plugin | the docker path only | [docker.com](https://docs.docker.com/get-docker/) |

## Step 1: Clone and Install

```bash
git clone https://github.com/OmniNode-ai/omnibase.git
cd omnibase
make install                        # the local path (asks first when run in a terminal)
# or
make install INSTALL_PATH=docker    # the self-hosted Docker path
```

`./install.sh --path local` and `./install.sh --path docker` do the same without
`make`. With no path given, the installer asks when it runs in a terminal and
uses `local` when it does not (an agent, CI, a pipe), so an unattended install
never waits on a prompt and never needs Docker. `--path cloud` is refused: the
cloud path is coming later.

This will:
- Check prerequisites; Docker and its Compose plugin are checked only on the docker path
- Resolve and export `OMNIBASE_PATH` for the install run (see "OMNIBASE_PATH" below)
- Clone all ONEX repositories into `repos/`
- Run `uv sync` for each Python repo (creates virtual environments, installs dependencies)
- Run `npm install` for the omnidash dashboard
- Install the Market skill package (`omnimarket`) into the `omnibase_infra` venv so
  `onex skill` can resolve Market nodes (see "Market Skill Nodes" below)
- Create a `.env` file from the template
- Write the runtime configuration for the chosen path (see "Install Path Configuration" below)

## Install Path Configuration

The installer writes the chosen path into the workspace runtime configuration,
`repos/config/onex/runtime/runtime_config.yaml`:

| Path | `event_bus.type` | Meaning |
|------|------------------|---------|
| `local` | `inmemory` | Everything runs in-process; state goes to local SQLite. No broker, no Docker. |
| `docker` | `kafka` | The shared Redpanda bus of the self-hosted stack (see "The Docker Path" below). |

It is the configuration the platform already reads, not an installer-only file:
`onex delegate` reads it whenever `OMNIBASE_PATH` is set, and the runtime reads it
when `ONEX_CONTRACTS_DIR` points at `repos/config/onex`. Its first two lines mark it
as installer-written and name the path.

### Switching Install Path

```bash
make switch-path INSTALL_PATH=docker   # or: ./install.sh --switch-path docker
make switch-path INSTALL_PATH=local    # or: ./install.sh --switch-path local
```

A switch rewrites only the runtime configuration: nothing is cloned or rebuilt.
Switching to `docker` checks for Docker first. `make status` prints the current
path. The installer never overwrites a runtime configuration it did not write: if
you replace the file with your own, a switch is refused and names the file.

## OMNIBASE_PATH

`OMNIBASE_PATH` is the canonical workspace root every cloned repo hangs off of
(`$OMNIBASE_PATH/<repo>`). `install.sh` and the `Makefile` derive it automatically
as `<this checkout>/repos` (never hardcoded) and export it for the install run and
for every `make` target. It is also appended to the generated `.env`, but `.env` is
not auto-sourced by your shell, so **export it yourself** before running
`onex`/`uv run` commands directly, outside `make`:

```bash
export OMNIBASE_PATH="$(pwd)/repos"
```

**What happens without it:**
- The omnimarket drift guard (`onex skill` / `onex node` / `onex delegate`
  pre-flight check) cannot locate `$OMNIBASE_PATH/omnimarket` to compare against,
  so it compares your installed packages against the version pins packaged inside
  those artifacts instead and reports that verdict. It does not refuse, and it is
  not silent: one structured line goes to stderr for every verdict, including the
  one meaning nothing could be compared.
- Nodes that need a workspace root hard-refuse rather than scanning nothing. For
  example `contract_sweep` exits with `OMNI_HOME is not set and no explicit
  omni_home was supplied — cannot resolve the default repo scope`.

If `OMNIBASE_PATH` cannot be derived (e.g. `install.sh` is piped via stdin instead
of run from a real checkout), `install.sh` fails fast with a clear error rather than
falling back to a default path.

**A second name, temporarily.** Some packaged tools — the omnimarket sweep and
orchestration nodes, and the Market skill co-install script — still read an
older spelling of this same root, `OMNI_HOME`. The installer and the `Makefile`
set both names to the same derived directory so following these instructions
cannot leave those tools unable to resolve a root. It is one directory with two
labels, not two settings to keep in step, and the second label goes away with
OMN-16856. Export `OMNIBASE_PATH`; if you run those nodes directly outside
`make`, export `OMNI_HOME` to the same value until then.

## Step 2: Configure Environment (docker path)

The `local` path needs no configuration here; skip to Step 4. On the `docker`
path, edit `.env` with your configuration:

```bash
# At minimum, set a Postgres password
POSTGRES_PASSWORD=your-secure-password
```

## Step 3: Create Environment File

```bash
make setup
```

This creates `.env` from `.env.example` if it does not already exist. It does **not** start Docker services. The `local` path does not use Docker; on the `docker` path, start the stack as described in "The Docker Path: Self-Hosted Infrastructure" below.

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

### The Docker Path: Self-Hosted Infrastructure

The `local` path needs none of this: in-memory bus and SQLite, no Docker, Kafka or Postgres. On the `docker` path (installed with `--path docker`, or switched to with `make switch-path INSTALL_PATH=docker`), the self-hosted stack is the laptop profile of `repos/omnibase_infra`: PostgreSQL, Redpanda, Valkey, the migrations and your own ONEX runtime (main and effects) in containers, under the compose project `omnibase-infra-local`. Every published port binds loopback, and it needs no credentials beyond two passwords it generates.

```bash
cd repos/omnibase_infra
make local-env      # writes ~/.omnibase/local.env and ~/.omnibase/local.bifrost.yaml (never overwrites)
```

Set the one line marked `model_endpoint` in `~/.omnibase/local.bifrost.yaml` to the
`/v1/chat/completions` URL of an OpenAI-compatible server for your model, then:

```bash
make up-local       # builds the runtime image and starts the stack; a cold start takes several minutes
make status-local   # migration gate, both runtime /health bodies, delegate consumer group
make delegate-local PROMPT="Reply with exactly one word: hello"
```

This brings up:
- **PostgreSQL** (port 5436) -- primary database
- **Redpanda** (port 19092) -- Kafka-compatible event bus
- **Valkey** (port 16379) -- Redis-compatible cache
- **Your ONEX runtime** (ports 8085 and 8086) -- main and effects

From the host, delegate through the stack with
`onex delegate "..." --bus kafka --kafka-bootstrap localhost:19092`. A bare
`onex delegate` with `OMNIBASE_PATH` set reads the `kafka` transport from the
runtime configuration and then refuses until you name the broker: the stack's
address is not yet declared in an overlay the host CLI reads.

To stop it:

```bash
cd repos/omnibase_infra && make down-local          # keeps its data
cd repos/omnibase_infra && make down-local-volumes  # deletes it
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

### Docker containers won't start (docker path)

Only the docker path uses Docker. Docker infrastructure is managed from `repos/omnibase_infra`. Check that Docker is running and that ports 5436, 19092, 16379, 8085 and 8086 are available:

```bash
lsof -i :5436
lsof -i :19092
lsof -i :16379
lsof -i :8085
lsof -i :8086
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

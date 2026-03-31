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
- Clone all ONEX repositories into `repos/`
- Run `uv sync` for each Python repo (creates virtual environments, installs dependencies)
- Run `npm install` for the omnidash dashboard
- Create a `.env` file from the template

## Step 2: Configure Environment

Edit `.env` with your configuration:

```bash
# At minimum, set a Postgres password
POSTGRES_PASSWORD=your-secure-password
```

## Step 3: Start Infrastructure

```bash
make setup
```

This starts the Docker infrastructure stack:
- **PostgreSQL** (port 5436) -- primary database
- **Redpanda** (port 19092) -- Kafka-compatible event bus
- **Valkey** (port 16379) -- Redis-compatible cache

## Step 4: Start Development

```bash
make dev
```

This starts the omnidash Next.js development server on port 3000 and shows available `onex` CLI commands.

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

### Stopping Infrastructure

```bash
make docker-down
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

## Architecture Overview

The ONEX platform is a distributed node-based system:

- **omnibase_core** provides the core contract model, node execution engine, and CLI
- **omnibase_infra** manages infrastructure (Postgres, Kafka, Valkey) and runtime services
- **omnibase_spi** defines the service provider interface that nodes implement
- **omniclaude** integrates Claude Code as an autonomous agent with hooks and skills
- **omnidash** is the real-time analytics dashboard (Next.js)
- **omniintelligence** provides AI-powered analysis nodes (intent detection, drift, review)
- **omnimemory** handles document ingestion and semantic search
- **onex_change_control** enforces governance and drift detection

## Troubleshooting

### Docker containers won't start

Check that Docker Desktop is running and ports 5436, 19092, and 16379 are available:

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

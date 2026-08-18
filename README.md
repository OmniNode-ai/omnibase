# ONEX Platform (omnibase)

One command to install and run the full ONEX node-based platform.

## Quick Start

```bash
git clone https://github.com/OmniNode-ai/omnibase.git
cd omnibase
make install
```

This clones all ONEX repositories, builds Python environments, installs dependencies, and makes the `onex` CLI available.

## What's Included

| Repository | Purpose |
|-----------|---------|
| omnibase_core | Core models, contracts, validators, CLI |
| omnibase_infra | Infrastructure services, Kafka, Postgres |
| omnibase_spi | Service provider interface protocols |
| omniclaude | Claude Code agent plugin, hooks, skills |
| omnidash | Composable widget dashboard (Vite + React) |
| omniintelligence | Intelligence nodes: intent, drift, review |
| omnimemory | Document ingestion + semantic retrieval |
| onex_change_control | Drift detection + governance |
| omnibase_compat | Shared structural package |

## Requirements

- Python 3.12+
- Node.js 20+
- Docker + Docker Compose
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Git

## Usage

```bash
# Install everything (clone repos, build envs, install deps)
make install

# Create .env from template (does NOT start Docker)
make setup

# Start development servers
make dev

# Run tests across all Python repos
make test

# Update all repos to latest main
make update

# Show repo versions and infrastructure health
make status
```

To start Docker infrastructure (PostgreSQL, Redpanda, Valkey), run from `repos/omnibase_infra`. `infra-up` is a shell function defined in `scripts/onex-cli.sh`, so source it first:

```bash
cd repos/omnibase_infra && source scripts/onex-cli.sh && infra-up
```

## Project Structure

```
omnibase/
├── README.md              # This file
├── Makefile               # All automation targets
├── install.sh             # One-command installer
├── .env.example           # Template environment file
├── repos.yaml             # Repository registry with metadata
└── docs/
    └── GETTING_STARTED.md # Detailed setup guide
```

## Environment Configuration

After installation, copy the example environment file and fill in your values:

```bash
cp .env.example .env
# Edit .env with your configuration
```

See [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) for detailed configuration instructions.

## License

Proprietary - OmniNode AI

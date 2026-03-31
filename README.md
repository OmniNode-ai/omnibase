# ONEX Platform (omnibase)

One command to install and run the full ONEX node-based platform.

## Quick Start

```bash
git clone https://github.com/OmniNode-ai/omnibase.git
cd omnibase
make install
```

This clones all ONEX repositories, builds Python environments, starts Docker infrastructure, and makes the `onex` CLI available.

## What's Included

| Repository | Purpose |
|-----------|---------|
| omnibase_core | Core models, contracts, validators, CLI |
| omnibase_infra | Infrastructure services, Kafka, Postgres |
| omnibase_spi | Service provider interface protocols |
| omniclaude | Claude Code agent plugin, hooks, skills |
| omnidash | Next.js analytics dashboard |
| omniintelligence | Intelligence nodes: intent, drift, review |
| omnimemory | Document ingestion + semantic retrieval |
| omninode_infra | API service, k8s manifests |
| omniweb | Landing page |
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

# Set up environment and start Docker infrastructure
make setup

# Start development servers
make dev

# Run tests across all Python repos
make test

# Update all repos to latest main
make update

# Show repo versions and infrastructure health
make status

# Start/stop Docker infrastructure
make docker-up
make docker-down
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

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
| omnimarket | Market skill nodes (resolved via `onex skill`) |
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

## Self-Hosted Infrastructure (Optional)

The default path above does not require Docker. To run the full self-hosted stack (PostgreSQL, Redpanda, Valkey), run from `repos/omnibase_infra`. `infra-up` is a shell function defined in `scripts/onex-cli.sh`, so source it first:

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

### OMNIBASE_PATH (required)

`make install` / `install.sh` derive `OMNIBASE_PATH` from the checkout location
(`<this repo>/repos`, where every sibling repo is cloned) and export it for
the install run and for every `make` target after it. It's also appended to
`.env`, but `.env` isn't auto-sourced by your shell — **export it yourself**
for any `onex`/`uv run` command you run directly (outside `make`):

```bash
export OMNIBASE_PATH="$(pwd)/repos"
```

Without it set: the omnimarket drift guard cannot locate a canonical clone to
compare against, so it falls back to comparing your installed packages against
the version pins packaged inside those artifacts, and reports that verdict on
stderr. It does not refuse, and it is not silent — every verdict, including
"nothing could be compared", is a line you can read. Nodes that need a
workspace root hard-refuse rather than scanning nothing; `contract_sweep`, for
example, exits with `OMNI_HOME is not set and no explicit omni_home was
supplied — cannot resolve the default repo scope`.

`install.sh`'s own derivation has no silent fallback — if it can't determine
its own checkout location (e.g. piped via stdin instead of run from a real
checkout) it fails fast with a clear error rather than guessing a path. That
fail-fast covers only the derivation, not what happens downstream once the
value is set to the wrong thing or left unset by hand.

**A second name, temporarily.** Some packaged tools — the omnimarket sweep and
orchestration nodes, and the Market skill co-install script — still read an
older spelling of this same root, `OMNI_HOME`. The installer and the `Makefile`
set both names to the same derived directory so following these instructions
cannot leave those tools unable to resolve a root. It is one directory with two
labels, not two settings to keep in step, and the second label goes away with
OMN-16856. Export `OMNIBASE_PATH`; if you run those nodes directly outside
`make`, export `OMNI_HOME` to the same value until then.

After installation, copy the example environment file and fill in your values:

```bash
cp .env.example .env
# Edit .env with your configuration
```

See [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) for detailed configuration instructions.

## License

[MIT](LICENSE) — consistent with every sibling repo this installer clones (`omnibase_core`, `omnibase_infra`, `omnibase_spi`, `omnibase_compat`, `omniclaude`, `omnidash`, `omniintelligence`, `omnimemory`, `omnimarket`, `onex_change_control`).

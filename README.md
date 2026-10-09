# ONEX Platform (omnibase)

One command to install and run the full ONEX node-based platform.

## Quick Start

**Most people should start with the PyPI quickstart**, not this repository:
[OmniClaude Quickstart](https://github.com/OmniNode-ai/knowledge_base/blob/main/guides/onex-plugin-quickstart.md)
(`guides/onex-plugin-quickstart.md`). It installs the `onex` command from PyPI
with one `uv tool install`: no clone, no Docker, about fifteen minutes.

This repository is the source install of the whole platform, for self-hosting
and for contributors:

```bash
git clone https://github.com/OmniNode-ai/omnibase.git
cd omnibase
make install                      # asks for the install path; local if there is no terminal
```

This clones all ONEX repositories, builds Python environments, installs dependencies, makes the
`onex` CLI available, and writes the runtime configuration for the install path you choose.

## Install Paths

| Path | What runs | Needs Docker | How to choose it |
|------|-----------|--------------|------------------|
| `local` (default) | Fully local runtime: in-memory event bus, local SQLite state | No | `make install` or `./install.sh --path local` |
| `docker` | Self-hosted Docker stack (PostgreSQL, Redpanda, Valkey) from `repos/omnibase_infra` | Yes | `make install INSTALL_PATH=docker` or `./install.sh --path docker` |
| `cloud` | Hosted runtime | — | Coming later; listed by the installer but not selectable yet |

**Docker is only for the `docker` path.** The installer checks for Docker and the
Docker Compose plugin only when you choose `docker`; the `local` path installs and
runs on a machine with no Docker at all. With no `--path` and no terminal to ask in
(an agent, CI, a pipe), the installer uses `local`.

The installer writes the chosen path into the workspace runtime configuration,
`repos/config/onex/runtime/runtime_config.yaml`: the in-memory bus for `local`,
the Kafka-compatible bus for `docker`. This is the file `onex delegate` reads when
`OMNIBASE_PATH` is set, and the file the runtime reads when `ONEX_CONTRACTS_DIR`
points at `repos/config/onex`. To move to the other path later, without
reinstalling:

```bash
make switch-path INSTALL_PATH=docker   # or: ./install.sh --switch-path docker
make switch-path INSTALL_PATH=local
```

The installer only rewrites a runtime configuration it wrote itself. If you
replace the file with your own, it is left alone and a switch is refused by name.

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

| Tool | Needed by |
|------|-----------|
| Python 3.12+ | every path |
| Node.js 20+ | every path (the omnidash dashboard) |
| [uv](https://docs.astral.sh/uv/) (Python package manager) | every path |
| Git | every path |
| Docker + Docker Compose plugin | the `docker` path only |

## Usage

```bash
# Install everything (clone repos, build envs, install deps) for an install path
make install                          # local, or asks in a terminal
make install INSTALL_PATH=docker      # self-hosted Docker stack

# Move an existing install to the other path (rewrites the runtime configuration only)
make switch-path INSTALL_PATH=docker

# Create .env from template (does NOT start Docker; its service settings are for the docker path)
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

## The Docker Path: Self-Hosted Infrastructure

The `local` path needs none of this. On the `docker` path, the self-hosted stack
is the laptop profile of `repos/omnibase_infra`: PostgreSQL, Redpanda, Valkey, the
migrations and your own ONEX runtime in containers, with every port bound to
loopback and no credentials beyond two passwords it generates:

```bash
cd repos/omnibase_infra
make local-env      # writes ~/.omnibase/local.env and ~/.omnibase/local.bifrost.yaml
# set your model's /v1/chat/completions URL on the model_endpoint line of ~/.omnibase/local.bifrost.yaml
make up-local       # builds the runtime image and starts the stack
make status-local   # migration gate, runtime health, delegate consumer
```

Delegations on this path run through your stack's runtime: `make delegate-local
PROMPT="..."` in `repos/omnibase_infra`. On the host, `onex delegate` with
`OMNIBASE_PATH` set reads the `kafka` transport from the runtime configuration
and then refuses until it is given a broker to address: the host CLI does not
yet read the stack's broker address from an overlay.

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

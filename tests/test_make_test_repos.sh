#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
#
# OMN-17427: `make test` runs the suites of the Python repos the platform is
# built from. The change-control repo is not one of them: the platform no longer
# depends on it at runtime, so the test loop must not name it. Reads the real
# Makefile through `make -n` (dry run: nothing is executed).
#
# Usage: bash tests/test_make_test_repos.sh
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

PASS=0
FAIL=0
ok()  { echo "  PASS: $*"; PASS=$((PASS + 1)); }
bad() { echo "  FAIL: $*"; FAIL=$((FAIL + 1)); }

PLAN="$(make -n -C "$HERE" test)" || { echo "FAIL: make -n test exited non-zero"; exit 1; }

# Positive control: the dry run did print the test loop and the core repo.
if grep -q 'omnibase_core' <<<"$PLAN"; then
    ok "make test loop lists omnibase_core"
else
    bad "make test loop does not list omnibase_core (dry run printed no loop)"
fi

if grep -q 'onex_change_control' <<<"$PLAN"; then
    bad "make test loop still names onex_change_control"
else
    ok "make test loop does not name onex_change_control"
fi

echo "passed=$PASS failed=$FAIL"
[ "$FAIL" -eq 0 ]

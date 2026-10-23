#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
#
# OMN-21309: runs every finish-step test and exits non-zero if any fails.
#
# Usage: bash tests/installer/test_finish_step.sh
set -uo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

rc=0
for t in disabled enabled name guards; do
    echo "== test_finish_step_$t.sh"
    bash "$DIR/test_finish_step_$t.sh" || rc=1
done
exit "$rc"

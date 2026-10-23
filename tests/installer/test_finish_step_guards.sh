#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
#
# OMN-21309 AC4: the finish step is skipped entirely, with the overlay key on,
# on a non-macOS host, in a non-interactive shell and over ssh. The control
# case (macOS, interactive, local) must run, so a guard that never lets the
# step through cannot pass.
#
# Usage: bash tests/installer/test_finish_step_guards.sh
set -uo pipefail
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"

overlay true
export ONEX_SKILL_OVERLAY_ROOTS="$WORK/overlay" FAKE_FULLNAME="Alice Example"

skipped() {
    local label="$1"
    if [ "$(calls_of say)" -eq 0 ] && [ "$(calls_of afplay)" -eq 0 ] && ! prompted; then
        ok "$label: step skipped"
    else
        bad "$label: step ran"
    fi
}

# Control: macOS, an interactive terminal, not over ssh.
( unset SSH_CONNECTION; FAKE_UNAME=Darwin HOME="$(home admin)" run_finish tty "" )
if [ "$(calls_of afplay)" -eq 1 ]; then ok "control: step runs"; else bad "control: step did not run"; fi

( unset SSH_CONNECTION; FAKE_UNAME=Linux HOME="$(home admin)" run_finish tty "" )
skipped "non-macOS host"

( unset SSH_CONNECTION; FAKE_UNAME=Darwin HOME="$(home admin)" run_finish notty "" )
skipped "non-interactive shell"

( FAKE_UNAME=Darwin SSH_CONNECTION="10.0.0.1 50000 10.0.0.2 22" HOME="$(home admin)" run_finish tty "" )
skipped "over ssh"

summary

#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
#
# OMN-21309 AC4: the finish step plays on every macOS install, in an
# interactive terminal, in a non-interactive shell and over ssh (a VM walk is
# run over ssh), and with no name it can find it still plays, without asking.
# It is skipped only on a non-macOS host.
#
# Usage: bash tests/installer/test_finish_step_guards.sh
set -uo pipefail
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"

overlay true
export ONEX_SKILL_OVERLAY_ROOTS="$WORK/overlay" FAKE_FULLNAME="Alice Example"

played() {
    local label="$1"
    if [ "$(calls_of afplay)" -eq 1 ]; then ok "$label: step plays"; else bad "$label: step did not play"; fi
}

( unset SSH_CONNECTION; FAKE_UNAME=Darwin HOME="$(home admin)" run_finish tty "" )
played "macOS, interactive, local"

( unset SSH_CONNECTION; FAKE_UNAME=Darwin HOME="$(home admin)" run_finish notty "" )
played "non-interactive shell"

( FAKE_UNAME=Darwin SSH_CONNECTION="10.0.0.1 50000 10.0.0.2 22" HOME="$(home admin)" run_finish tty "" )
played "over ssh"

( FAKE_UNAME=Darwin SSH_CONNECTION="10.0.0.1 50000 10.0.0.2 22" HOME="$(home admin)" run_finish notty "" )
played "over ssh, non-interactive"

( FAKE_FULLNAME="" FAKE_UNAME=Darwin SSH_CONNECTION="10.0.0.1 50000 10.0.0.2 22" HOME="$(home admin)" run_finish notty "" )
played "no name found, non-interactive"
if prompted; then bad "no name found, non-interactive: asked for a name"; else ok "no name found, non-interactive: did not ask"; fi

( unset SSH_CONNECTION; FAKE_UNAME=Linux HOME="$(home admin)" run_finish tty "" )
if [ "$(calls_of say)" -eq 0 ] && [ "$(calls_of afplay)" -eq 0 ] && ! prompted; then
    ok "non-macOS host: step skipped"
else
    bad "non-macOS host: step ran"
fi

summary

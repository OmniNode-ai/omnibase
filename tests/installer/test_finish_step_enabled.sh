#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
#
# OMN-21309 AC2: with finish_greeting_enabled: "true" in the first onboarding
# overlay under ONEX_SKILL_OVERLAY_ROOTS, the finish step builds exactly one
# clip and plays it exactly once. A later root that says "false" is ignored,
# because only the first overlay counts.
#
# Usage: bash tests/installer/test_finish_step_enabled.sh
set -uo pipefail
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"

export FAKE_FULLNAME="Alice Example" FAKE_UNAME=Darwin
unset SSH_CONNECTION
overlay true
mkdir -p "$WORK/second/node_onboarding"
echo 'finish_greeting_enabled: "false"' > "$WORK/second/node_onboarding/overlay.yaml"
export ONEX_SKILL_OVERLAY_ROOTS="$WORK/overlay:$WORK/second"

HOME="$(home admin)" run_finish tty ""

n="$(calls_of say)"
if [ "$n" -eq 1 ]; then ok "one clip built (say invoked once)"; else bad "say invoked $n times, expected 1"; fi
n="$(calls_of afplay)"
if [ "$n" -eq 1 ]; then ok "clip played once (afplay invoked once)"; else bad "afplay invoked $n times, expected 1"; fi
if grep -q "^afplay .*/finish.wav" "$CALLS"; then ok "afplay played the joined clip"; else bad "afplay did not play finish.wav"; fi

summary

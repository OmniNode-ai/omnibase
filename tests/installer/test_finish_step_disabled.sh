#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
#
# OMN-21309: with the overlay key set to "false", the finish step prompts for
# no name and invokes neither `say` nor `afplay`, even on an interactive macOS
# terminal where it would otherwise run. "false" is the only way to turn it off.
#
# Usage: bash tests/installer/test_finish_step_disabled.sh
set -uo pipefail
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"

export FAKE_FULLNAME="" FAKE_UNAME=Darwin
unset SSH_CONNECTION

for case_ in "false" "false-uppercase"; do
    case "$case_" in
        false)           overlay false; export ONEX_SKILL_OVERLAY_ROOTS="$WORK/overlay" ;;
        false-uppercase) overlay none; echo 'finish_greeting_enabled: "FALSE"' > "$WORK/overlay/node_onboarding/overlay.yaml"
                         export ONEX_SKILL_OVERLAY_ROOTS="$WORK/overlay" ;;
    esac
    # The home folder name does not read as a name, so an enabled step would
    # have to prompt: a prompt here would show.
    HOME="$(home admin)" run_finish tty $'Sam\n'
    if prompted; then bad "$case_: prompted for a name"; else ok "$case_: no name prompt"; fi
    if [ "$(calls_of say)" -eq 0 ]; then ok "$case_: say not invoked"; else bad "$case_: say invoked"; fi
    if [ "$(calls_of afplay)" -eq 0 ]; then ok "$case_: afplay not invoked"; else bad "$case_: afplay invoked"; fi
done

summary

#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
#
# OMN-21309: the finish step is on by default. With no overlay roots, no
# overlay file, or an overlay that does not name the field, an interactive
# macOS install builds one clip and plays it once.
#
# Usage: bash tests/installer/test_finish_step_default_on.sh
set -uo pipefail
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"

export FAKE_FULLNAME="Alice Example" FAKE_UNAME=Darwin
unset SSH_CONNECTION

for case_ in "no-roots" "no-overlay-file" "no-field"; do
    case "$case_" in
        no-roots)        unset ONEX_SKILL_OVERLAY_ROOTS ;;
        no-overlay-file) overlay none; export ONEX_SKILL_OVERLAY_ROOTS="$WORK/overlay" ;;
        no-field)        overlay none; echo "other: 1" > "$WORK/overlay/node_onboarding/overlay.yaml"
                         export ONEX_SKILL_OVERLAY_ROOTS="$WORK/overlay" ;;
    esac
    HOME="$(home admin)" run_finish tty ""
    if [ "$(calls_of say)" -ge 1 ]; then ok "$case_: clip built"; else bad "$case_: say not invoked"; fi
    if [ "$(calls_of afplay)" -ge 1 ]; then ok "$case_: clip played"; else bad "$case_: afplay not invoked"; fi
done

summary

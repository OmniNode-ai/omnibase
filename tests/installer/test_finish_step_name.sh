#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
#
# OMN-21309 AC3: the name comes from `id -F`, then the home folder's name when it
# reads as a name, then one interactive prompt, and never from the git name.
#
# Usage: bash tests/installer/test_finish_step_name.sh
set -uo pipefail
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"

export FAKE_UNAME=Darwin
unset SSH_CONNECTION
overlay true
export ONEX_SKILL_OVERLAY_ROOTS="$WORK/overlay"

# 1. id -F answers: its first word wins, and no prompt is shown.
FAKE_FULLNAME="alice example" HOME="$(home bob)" run_finish tty ""
if finish_name_was Alice; then ok "id -F: name is Alice"; else bad "id -F: expected Alice; got $(grep FINISH_NAME "$OUT")"; fi
if prompted; then bad "id -F: prompted although id -F answered"; else ok "id -F: no prompt"; fi

# 2. id -F is empty, the home folder reads as a name.
FAKE_FULLNAME="" HOME="$(home bob)" run_finish tty ""
if finish_name_was Bob; then ok "home folder: name is Bob"; else bad "home folder: expected Bob; got $(grep FINISH_NAME "$OUT")"; fi
if prompted; then bad "home folder: prompted although the folder name reads as a name"; else ok "home folder: no prompt"; fi

# 3. Neither answers: one prompt, and its answer is used.
FAKE_FULLNAME="" HOME="$(home admin)" run_finish tty $'carol\n'
if prompted; then ok "prompt: asked once"; else bad "prompt: no prompt shown"; fi
if finish_name_was Carol; then ok "prompt: name is Carol"; else bad "prompt: expected Carol; got $(grep FINISH_NAME "$OUT")"; fi

# 4. Only a git name is set, and the prompt is left empty: the git name is
#    never used, so the step has no name and builds nothing.
h="$(home admin)"
printf '[user]\n\tname = Gitname Person\n' > "$h/.gitconfig"
FAKE_FULLNAME="" HOME="$h" run_finish tty $'\n'
if finish_name_was ""; then ok "git name only: no name chosen"; else bad "git name only: got $(grep FINISH_NAME "$OUT")"; fi
if grep -qi "gitname" "$OUT" "$CALLS"; then bad "git name only: the git name was used"; else ok "git name only: git name never used"; fi
if [ "$(calls_of say)" -eq 0 ] && [ "$(calls_of afplay)" -eq 0 ]; then
    ok "git name only: nothing built or played"
else
    bad "git name only: say or afplay ran without a name"
fi

summary

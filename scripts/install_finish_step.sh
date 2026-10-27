#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
#
# The installer's finish step, sourced by install.sh. It expects SCRIPT_DIR (the
# omnibase checkout) and a warn() function from its caller, and defines
# finish_prepare (run once near the start of the install) and finish_greeting
# (run once at the very end). tests/installer drives it directly.

# ------------------------------------------------------------------
# Finish greeting (every macOS install, local or over ssh)
# ------------------------------------------------------------------
# The user's first name, found from the macOS account's full name, else the
# home directory's name when it reads as a name, else asked once when stdin is
# a terminal. Spoken at the end of the install; with no name the clip plays
# without one. afplay and say are part of macOS and play on the Mac's own audio
# output, so an ssh session (a VM walk) plays it too.
#
# On by default. A deployment overlay can turn it off. The overlay is the
# onboarding node's, found the way every node overlay is found (OMN-20935): the
# first <root>/node_onboarding/overlay.yaml under the roots that
# ONEX_SKILL_OVERLAY_ROOTS lists, colon separated. Its field
#   finish_greeting_enabled: "false"
# turns it off; an absent variable, file or field, or "true", leaves it on,
# and any other value is named in a warning and leaves it on.
FINISH_DIR="$SCRIPT_DIR/assets/finish"
FINISH_OVERLAY_NODE="node_onboarding"
FINISH_OVERLAY_FIELD="finish_greeting_enabled"
finish_name=""

# Prints the first <root>/node_onboarding/overlay.yaml in root order.
finish_overlay_file() {
    local rest="${ONEX_SKILL_OVERLAY_ROOTS:-}" root
    while [ -n "$rest" ]; do
        root="${rest%%:*}"
        if [ "$root" = "$rest" ]; then rest=""; else rest="${rest#*:}"; fi
        if [ -n "$root" ] && [ -f "$root/$FINISH_OVERLAY_NODE/overlay.yaml" ]; then
            printf '%s\n' "$root/$FINISH_OVERLAY_NODE/overlay.yaml"
            return 0
        fi
    done
    return 1
}

finish_greeting_enabled() {
    local file line value
    file="$(finish_overlay_file)" || return 0
    line="$(grep -E "^$FINISH_OVERLAY_FIELD:" "$file" 2>/dev/null | tail -n 1 || true)"
    [ -n "$line" ] || return 0
    value="${line#"$FINISH_OVERLAY_FIELD":}"
    value="$(printf '%s' "${value%%#*}" | tr -d "[:space:]\"'" | tr '[:upper:]' '[:lower:]')"
    case "$value" in
        true) return 0 ;;
        false) return 1 ;;
        *)
            warn "$file: $FINISH_OVERLAY_FIELD must be \"true\" or \"false\", not '$value'; leaving it on."
            return 0
            ;;
    esac
}

name_like() {
    case "$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]')" in
        ""|admin|administrator|user|users|mac|macbook|macuser|test|guest|root|dev|developer|owner|me|home|runner|ci|build|staff|default|shared) return 1 ;;
    esac
    printf '%s' "$1" | grep -Eq "^[A-Za-z][A-Za-z'-]{1,19}$"
}

capitalize() {
    printf '%s%s' "$(printf '%s' "${1:0:1}" | tr '[:lower:]' '[:upper:]')" "${1:1}"
}

finish_greeting_ready() {
    [ "$(uname -s)" = "Darwin" ] \
        && [ -f "$FINISH_DIR/welcome.wav" ] && [ -f "$FINISH_DIR/to-omninode.wav" ] \
        && command -v afplay >/dev/null && command -v say >/dev/null && command -v python3 >/dev/null
}

# Builds one clip (recorded welcome, the name in the Fred voice, recorded
# close) so it plays in a single afplay: each afplay adds about a second of
# silence, so playing the pieces one by one leaves long gaps.
build_finish_clip() {
    local work="$1" parts=("$FINISH_DIR/welcome.wav")
    if [ -n "$finish_name" ]; then
        say -v Fred --file-format=WAVE --data-format=LEI16@22050 -o "$work/name.wav" "$finish_name" || return 1
        parts+=("$work/name.wav")
    fi
    python3 - "${parts[@]}" "$FINISH_DIR/to-omninode.wav" "$work/finish.wav" <<'PY'
import array, sys, wave
*parts, out = sys.argv[1:]
rate, samples = None, array.array("h")
for i, path in enumerate(parts):
    with wave.open(path) as w:
        rate = rate or w.getframerate()
        a = array.array("h", w.readframes(w.getnframes()))
    loud = [j for j, s in enumerate(a) if abs(s) > 500] or [0, len(a) - 1]
    pad = rate // 100
    samples.extend(a[max(loud[0] - pad, 0): loud[-1] + pad])
    if i < len(parts) - 1:
        samples.extend([0] * int(rate * 0.04))
with wave.open(out, "wb") as o:
    o.setnchannels(1); o.setsampwidth(2); o.setframerate(rate); o.writeframes(samples.tobytes())
PY
}

finish_work=""

# Resolves the name and starts building the clip in the background. Called once,
# near the start of the install; does nothing when the step is off or the host
# does not qualify.
finish_prepare() {
    finish_greeting_enabled && finish_greeting_ready || return 0
    local candidate
    candidate="$(id -F 2>/dev/null | awk '{print $1}')"
    name_like "$candidate" || candidate="$(basename "$HOME")"
    if name_like "$candidate"; then
        finish_name="$(capitalize "$candidate")"
    elif [ -t 0 ]; then
        read -r -p "What should we call you? " candidate
        candidate="$(printf '%s' "$candidate" | awk '{print $1}')"
        name_like "$candidate" && finish_name="$(capitalize "$candidate")"
    fi
    finish_work="$(mktemp -d)"
    (build_finish_clip "$finish_work" >/dev/null 2>&1 &)
}

finish_greeting() {
    [ -n "$finish_work" ] && [ -f "$finish_work/finish.wav" ] && finish_greeting_ready || return 0
    afplay "$finish_work/finish.wav" 2>/dev/null || true
    rm -rf "$finish_work"
}

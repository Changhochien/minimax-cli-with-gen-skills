#!/bin/bash
# Install minimax CLI tool and Claude Code skill
#
# One-liner (no clone required):
#   curl -sL https://raw.githubusercontent.com/Changhochien/minimax/main/install.sh | bash -s -- --key YOUR_KEY
#
# Or clone first:
#   gh repo clone Changhochien/minimax && cd minimax
#   ./install.sh --key YOUR_KEY
#
# Options:
#   --key <KEY>        MiniMax API key (required unless --skills-only)
#   --host global|cn   API region (default: global)
#   --skills-only      Only install the skill, skip CLI

set -e

echo "=== minimax installer ==="
echo ""

# Determine script directory — works whether run as ./install.sh or via curl|bash
if [ -n "$SCRIPT_DIR" ] && [ -d "$SCRIPT_DIR/.claude" ]; then
    : # Already set and valid
elif [ -n "$0" ] && [ -d "$(dirname "$0")/.claude" ]; then
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
else
    # Running via curl|bash — clone to temp dir
    echo "(Detected curl|bash invocation, cloning repo to temp dir...)"
    TMPDIR=$(mktemp -d)
    git clone --depth 1 https://github.com/Changhochien/minimax "$TMPDIR"
    SCRIPT_DIR="$TMPDIR"
fi

# Check for uv
if ! command -v uv &>/dev/null; then
    echo "Error: uv is required. Install: https://github.com/astral-sh/uv"
    exit 1
fi

# Parse arguments
API_KEY=""
HOST="global"
SKILLS_ONLY=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --key)
            API_KEY="$2"
            shift 2
            ;;
        --key=*)
            API_KEY="${1#*=}"
            shift
            ;;
        --host)
            HOST="$2"
            shift 2
            ;;
        --host=*)
            HOST="${1#*=}"
            shift
            ;;
        --skills-only)
            SKILLS_ONLY=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--key <KEY>] [--host global|cn] [--skills-only]"
            exit 1
            ;;
    esac
done

if [ "$HOST" != "global" ] && [ "$HOST" != "cn" ]; then
    echo "Error: --host must be 'global' or 'cn'"
    exit 1
fi

# Install CLI (unless --skills-only)
if [ "$SKILLS_ONLY" = false ]; then
    if [ -z "$API_KEY" ]; then
        echo "Error: API key required (or use --skills-only to skip CLI install)"
        exit 1
    fi
    echo "Installing minimax CLI..."
    uv tool install --from "git+https://github.com/Changhochien/minimax" minimax

    # Save API key and host to config file
    CONFIG_DIR="$HOME/.config/minimax"
    mkdir -p "$CONFIG_DIR"
    cat > "$CONFIG_DIR/creds.toml" <<EOF
MINIMAX_API_KEY=$API_KEY
MINIMAX_API_HOST=$HOST
EOF

    if [ "$HOST" = "cn" ]; then
        echo "Using Mainland China API endpoint (api.minimaxi.com)"
    else
        echo "Using Global API endpoint (api.minimax.io)"
    fi
fi

# Install Claude Code skill
SKILL_SRC="$SCRIPT_DIR/.claude/skills/minimax"
SKILL_DEST="$HOME/.claude/skills/minimax"

if [ -d "$SKILL_SRC" ]; then
    echo "Installing Claude Code skill..."
    mkdir -p "$HOME/.claude/skills"
    cp -r "$SKILL_SRC" "$SKILL_DEST"
    echo "Skill installed to ~/.claude/skills/minimax/"
else
    echo "Note: No Claude Code skill found"
fi

echo ""
echo "=== Done ==="
if [ "$SKILLS_ONLY" = false ]; then
    echo "Config saved to ~/.config/minimax/creds.toml"
fi
echo ""
echo "Usage:"
echo "  minimax image generate --prompt 'A rubber belt' --aspect-ratio 16:9"
echo "  minimax speech synthesize --text 'Hello' --voice-id Deep_Voice_Man"
echo "  minimax video generate --prompt 'Conveyor belt in motion'"
echo "  minimax music generate --prompt 'Upbeat corporate' --instrumental"
echo ""
echo "In Claude Code: invoke the 'minimax' skill to auto-route to the right subcommand."

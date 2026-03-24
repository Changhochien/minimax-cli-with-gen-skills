#!/bin/bash
# Install minimax for Claude Code (MCP server)
#
# Usage:
#   gh repo clone Changhochien/minimax && cd minimax
#   ./install.sh --key YOUR_KEY              # user-scope (default)
#   ./install.sh --key YOUR_KEY --project     # project-scope (writes to .mcp.json)
#
# For project-scope: run inside a Claude Code project directory.

set -e

echo "=== minimax installer ==="
echo ""

# Check for uv
if ! command -v uv &>/dev/null; then
    echo "Error: uv is required. Install: https://github.com/astral-sh/uv"
    exit 1
fi

# Check for claude
if ! command -v claude &>/dev/null; then
    echo "Error: Claude Code CLI is required. Install: https://claude.ai/code"
    exit 1
fi

# Parse arguments
API_KEY=""
SCOPE="user"
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
        --project)
            SCOPE="project"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--key <KEY>] [--project]"
            exit 1
            ;;
    esac
done

if [ -z "$API_KEY" ]; then
    echo "Error: API key is required. Run: $0 --key YOUR_KEY"
    exit 1
fi

SCOPE_FLAG=""
if [ "$SCOPE" = "project" ]; then
    SCOPE_FLAG="-s project"
    echo "Scope: project (.mcp.json)"
else
    echo "Scope: user (~/.claude.json)"
fi

echo ""
echo "Registering MCP server..."
claude mcp add-json $SCOPE_FLAG minimax "$(cat <<EOF
{
  "type": "stdio",
  "command": "uvx",
  "args": ["--from", "git+https://github.com/Changhochien/minimax", "minimax"],
  "env": { "MINIMAX_API_KEY": "$API_KEY" }
}
EOF
)"

echo ""
echo "=== Done ==="
echo "Restart Claude Code, then use MCP tools:"
echo "  mcp__minimax__generate_image()"
echo "  mcp__minimax__synthesize_speech()"
echo "  mcp__minimax__generate_video()"
echo ""
echo "Or install the CLI:"
echo "  uv tool install --from 'git+https://github.com/Changhochien/minimax' minimax"

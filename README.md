# minimax

Unified MiniMax CLI and MCP server — image generation, text-to-speech, and video generation in one package.

## Modules

| Module | Model | Description |
|--------|-------|-------------|
| **Image** | `image-01` | Text-to-Image, Image-to-Image, character-consistent I2I |
| **Speech** | `speech-2.8-hd` | TTS, voice cloning, voice design, async long-form TTS |
| **Video** | `MiniMax-Hailuo-02` | Text-to-Video, Image-to-Video, first-last-frame, subject-consistent |

## Prerequisites

- [uv](https://github.com/astral-sh/uv)
- [Claude Code](https://claude.ai/code)
- MiniMax API key with Token Plan enabled — get one at [platform.minimax.io](https://platform.minimax.io)

## Install

```bash
curl -sL https://raw.githubusercontent.com/Changhochien/minimax/main/install.sh | bash -s -- --key YOUR_MINIMAX_KEY
```

Or clone and run:

```bash
gh repo clone Changhochien/minimax
cd minimax
chmod +x install.sh
./install.sh --key YOUR_MINIMAX_KEY
```

### User scope (default)
Installs to `~/.claude.json` — MCP available in all Claude Code sessions.

### Project scope
Installs to `.mcp.json` in the current directory:

```bash
./install.sh --key YOUR_MINIMAX_KEY --project
```

**Restart Claude Code** after installation.

## Manual MCP install

```bash
claude mcp add-json minimax '{
  "type": "stdio",
  "command": "uvx",
  "args": ["--from", "git+https://github.com/Changhochien/minimax", "minimax"],
  "env": { "MINIMAX_API_KEY": "your-key" }
}'
```

## CLI install

```bash
# User-wide (requires uv)
uv tool install --from "git+https://github.com/Changhochien/minimax" minimax

# Or via pip
pip install git+https://github.com/Changhochien/minimax
```

## CLI Usage

```bash
# Image generation (T2I)
minimax image generate --prompt "A precision rubber belt on white" --aspect-ratio 16:9

# Image generation (I2I)
minimax image generate --prompt "Same product on dark industrial background" \\
  --image https://example.com/photo.jpg --aspect-ratio 16:9

# Text-to-speech
minimax speech synthesize --text "Welcome to our product line" --voice-id Deep_Voice_Man --emotion calm

# Async long-form TTS
minimax speech long-create --text "$(cat long-text.txt)" --voice-id English_Insightful_Speaker
minimax speech long-query <task_id>

# Voice cloning
minimax speech upload --audio https://example.com/ceo-voice.mp3
minimax speech clone --file-id <file_id> --voice-id ceo_voice

# Voice design
minimax speech design --prompt "Warm professional female narrator" \\
  --preview "Precision rubber belts." --voice-id narrator_voice

# Video generation (T2V)
minimax video generate --prompt "A factory conveyor belt in motion"

# Video generation (I2V)
minimax video generate --prompt "The product slowly rotating" \\
  --first-frame https://example.com/product-shot.jpg

# Poll video task
minimax video query <task_id>
```

### List voices
```bash
minimax speech list-voices
```

## MCP Tools

Once installed, call these tools in Claude Code:

```
mcp__minimax__generate_image(...)      # Image (T2I / I2I)
mcp__minimax__synthesize_speech(...)   # TTS
mcp__minimax__create_long_speech_task(...) + query_long_speech_task(...)
mcp__minimax__upload_audio(...) + clone_voice(...)
mcp__minimax__design_voice(...)
mcp__minimax__get_voice(...) / delete_voice(...) / list_voices()
mcp__minimax__generate_video(...)      # Video (T2V / I2V)
mcp__minimax__query_video_task(...)
mcp__minimax__retrieve_video_file(...)
```

## Uninstall

```bash
claude mcp remove minimax
```

Restart Claude Code.

## Development

```bash
gh repo clone Changhochien/minimax
cd minimax

# Test MCP server
uv run fastmcp dev src/minimax/mcp/__init__.py

# Test CLI
uv run python src/minimax_cli.py --help
```

## Architecture

```
minimax/
├── src/
│   ├── minimax/           # Shared Python package
│   │   ├── api/           # HTTP client (httpx)
│   │   ├── image/         # Image generation
│   │   ├── speech/        # TTS + voice cloning/design
│   │   ├── video/         # Video generation
│   │   └── mcp/           # FastMCP server
│   └── minimax_cli.py     # Typer CLI entry point
├── pyproject.toml
├── README.md
└── install.sh
```

Both the CLI and MCP server share the same `minimax.*` Python package — no duplicated API code.

## API Details

### Image
- **Endpoint:** `POST https://api.minimax.io/v1/image_generation`
- **Model:** `image-01`
- **Token Plan quotas (daily images):** Plus 50, Max 120, Plus-Highspeed 100, Max-Highspeed 200, Ultra-Highspeed 800

### Speech
- **T2A Endpoint:** `POST https://api.minimax.io/v1/t2a_v2`
- **Async TTS:** `POST https://api.minimax.io/v1/t2a_async_v2` + `GET /query/t2a_async_query_v2`
- **Voice Clone:** `POST /files/upload` + `POST /voice_clone`
- **Voice Design:** `POST /voice_design`
- **Models:** `speech-2.8-hd`, `speech-2.8-turbo`, `speech-2.6-hd`, `speech-02-hd`, etc.
- **Token Plan quotas (daily chars):** Plus 4,000, Max 11,000, Plus-Highspeed 9,000, Max-Highspeed 19,000, Ultra-Highspeed 50,000

### Video
- **Generate:** `POST https://api.minimax.io/v1/video_generation`
- **Query:** `GET https://api.minimax.io/v1/query/video_generation`
- **Retrieve:** `GET https://api.minimax.io/v1/files/retrieve`
- **Models:** `MiniMax-Hailuo-2.3`, `MiniMax-Hailuo-02`, `S2V-01`

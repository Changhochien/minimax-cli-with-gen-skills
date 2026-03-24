# minimax

MiniMax CLI — image generation, text-to-speech, and video generation.

Designed for Claude Code and OpenClaw: zero MCP token overhead, skills call the CLI directly.

## Modules

| Module | Model | Description |
|--------|-------|-------------|
| **Image** | `image-01` | Text-to-Image, Image-to-Image, character-consistent I2I |
| **Speech** | `speech-2.8-hd` | TTS, voice cloning, voice design, async long-form TTS |
| **Video** | `MiniMax-Hailuo-02` | Text-to-Video, Image-to-Video, first-last-frame, subject-consistent |

## Prerequisites

- [uv](https://github.com/astral-sh/uv)
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

This installs `minimax` as a CLI tool via `uv tool install` and saves your API key to `~/.config/minimax/creds.toml`.

## Manual install

```bash
# CLI tool
uv tool install --from "git+https://github.com/Changhochien/minimax" minimax

# Set API key
export MINIMAX_API_KEY=your-key
# Or save to ~/.config/minimax/creds.toml
```

## Usage

```bash
# Image generation (T2I)
minimax image generate --prompt "A precision rubber belt on white" --aspect-ratio 16:9

# Image generation (I2I)
minimax image generate --prompt "Same product on dark industrial background" \
  --image https://example.com/photo.jpg --aspect-ratio 16:9

# Character-consistent I2I
minimax image generate --prompt "Same person in a factory uniform" \
  --image https://example.com/product-photo.jpg \
  --subject-ref https://example.com/portrait.jpg

# Save image to file
minimax image generate --prompt "Product hero shot" --aspect-ratio 16:9 --output hero.jpg

# Text-to-speech
minimax speech synthesize --text "Welcome to our product line" --voice-id Deep_Voice_Man --emotion calm

# Async long-form TTS (for texts >10,000 chars)
minimax speech long-create --text "$(cat long-text.txt)" --voice-id English_Insightful_Speaker
minimax speech long-query <task_id>

# Voice cloning
minimax speech upload --audio https://example.com/ceo-voice.mp3
minimax speech clone --file-id <file_id> --voice-id ceo_voice

# Voice design
minimax speech design --prompt "Warm professional female narrator" \
  --preview "Precision rubber belts." --voice-id narrator_voice

# List preset voices
minimax speech list-voices

# Video generation (T2V)
minimax video generate --prompt "A factory conveyor belt in motion"

# Video generation (I2V)
minimax video generate --prompt "The product slowly rotating" \
  --first-frame https://example.com/product-shot.jpg

# Video with first and last frame
minimax video generate --prompt "Product transitions from day to night" \
  --first-frame https://example.com/day.jpg \
  --last-frame https://example.com/night.jpg

# Poll video task
minimax video query <task_id>

# Retrieve generated video file
minimax video retrieve <file_id>
```

## Claude Code Integration

This CLI is designed to be called by Claude Code Skills. A skill instructs Claude to invoke `minimax` via the Bash tool — zero MCP tool schema overhead.

Example skill instruction:
```
Use the minimax CLI to generate images:
  minimax image generate --prompt "<description>" --aspect-ratio 16:9
```

See the `.claude/skills/` directory in your project for MiniMax skill files.

## Uninstall

```bash
uv tool uninstall minimax
```

## Development

```bash
gh repo clone Changhochien/minimax
cd minimax

# Test CLI
uv run python src/minimax_cli.py --help
uv run python src/minimax_cli.py image --help
uv run python src/minimax_cli.py speech --help
uv run python src/minimax_cli.py video --help
```

## Architecture

```
minimax/
├── src/
│   ├── minimax/           # Shared Python package
│   │   ├── api/           # HTTP client (httpx)
│   │   ├── image/         # Image generation
│   │   ├── speech/        # TTS + voice cloning/design
│   │   └── video/         # Video generation
│   └── minimax_cli.py     # Typer CLI entry point
├── pyproject.toml
├── README.md
└── install.sh
```

The CLI and shared API layer are in the same package — no duplicated code.

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

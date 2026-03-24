# Image Generation Reference

**CLI:** `minimax image generate [options]`

## Parameters

| Flag | Default | Description |
|------|---------|-------------|
| `--prompt, -p` | required | Image description |
| `--aspect-ratio, -r` | null | `1:1`, `16:9`, `9:16`, `4:3`, `3:2`, `2:3`, `3:4`, `21:9` |
| `--width` | null | Custom width (512–2048, divisible by 8). Note: 2048x2048 square is rejected by the API; max square is ~1792x1792. |
| `--height` | null | Custom height (512–2048, divisible by 8). Note: 2048x2048 square is rejected by the API; max square is ~1792x1792. |
| `--model, -m` | `image-01` | Model identifier |
| `--response-format, -f` | `base64` | `base64` or `url` |
| `--number, -n` | `1` | Number of images (1–9) |
| `--image, -i` | null | Reference image URL or base64 for I2I |
| `--subject-ref` | null | Portrait URL for character-consistent I2I |
| `--seed, -s` | null | Integer seed for reproducible results |
| `--optimizer` | false | Enable prompt optimizer |
| `--output, -o` | null | Write first image to file |

## Modes

**T2I:** `--prompt` only
**I2I:** `--prompt` + `--image <url or base64>`
**Character-consistent I2I:** Add `--subject-ref <portrait-url>`

## Examples

```bash
# Product hero (T2I)
minimax image generate \
  --prompt "A precision rubber belt on white background, studio lighting" \
  --aspect-ratio 16:9 --output belt.jpg

# Transform to industrial background (I2I)
minimax image generate \
  --prompt "Same product on dark industrial background" \
  --image https://example.com/product.jpg --aspect-ratio 16:9

# Character-consistent portrait
minimax image generate \
  --prompt "Same person wearing factory uniform" \
  --image https://example.com/photo.jpg \
  --subject-ref https://example.com/portrait.jpg
```

# Text-to-Speech (Edge TTS)

This module converts text files to speech audio using Microsoft Edge TTS, offering more natural voices compared to Kokoro.

## Advantages over Kokoro

- **More natural voices**: Microsoft's neural voices are highly realistic
- **Better Spanish support**: Multiple regional accents (Spain, Mexico, Argentina)
- **SSML support**: Fine-grained control over emphasis, pitch, and pauses
- **No GPU required**: Works on CPU efficiently
- **Free**: No API keys or costs

## Installation

```bash
pip install -r tts/requirements.txt
```

## Usage

```bash
python tts/tts2.py <file_path> [options]
```

### Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `file_path` | Path to the input text file (required) | - |
| `--output-dir` | Output subdirectory inside `dialog/` folder | `dialog/` |
| `--voice` | Voice name to use | `es-ES-ElviraNeural` |
| `--list-voices` | List available Spanish voices | - |

### Examples

Basic usage:
```bash
python tts/tts2.py story/chapter1.txt
```

List available voices:
```bash
python tts/tts2.py --list-voices
```

Custom voice:
```bash
python tts/tts2.py story/chapter1.txt --voice es-MX-DaliaNeural
```

Custom output directory:
```bash
python tts/tts2.py story/chapter1.txt --output-dir chapter1 --voice es-ES-AlvaroNeural
```

## Output

The generated audio file will be saved as `tts/dialog/<filename>.wav` by default.

If you specify `--output-dir`, it will be saved as `tts/dialog/<output-dir>/<filename>.wav`.

For example, running:
```bash
python tts/tts2.py story/chapter1.txt --output-dir chapter1
```

Will generate: `tts/dialog/chapter1/chapter1.wav`

## Available Voices

| Voice | Description |
|-------|-------------|
| `es-ES-ElviraNeural` | Female Spanish (Spain) |
| `es-ES-AlvaroNeural` | Male Spanish (Spain) |
| `es-MX-DaliaNeural` | Female Spanish (Mexico) |
| `es-MX-JorgeNeural` | Male Spanish (Mexico) |
| `es-AR-ElenaNeural` | Female Spanish (Argentina) |
| `es-AR-TomasNeural` | Male Spanish (Argentina) |

For a full list, run: `python tts/tts2.py --list-voices`

## Custom Pronunciations

You can add custom pronunciations in `tts/pronunciations.yml`. The file already includes common Magic: The Gathering terms.

```yaml
planeswalker: plensuóker
eldrazi: eldrasi
zendikar: sendikár
```

The script automatically handles capitalized versions of words.

## SSML Features

Edge TTS uses SSML (Speech Synthesis Markup Language) for advanced control:

### Pause Durations

| Punctuation | Duration |
|-------------|----------|
| Newline (`\n`) | 1000ms |
| Ellipsis (`...`) | 800ms |
| Period (`.`) | 600ms |
| Question (`?`) | 400ms |
| Exclamation (`!`) | 300ms |
| Comma (`,`) | 200ms |

### Prosody Modifiers

The script automatically adjusts rate and pitch based on punctuation:

| Punctuation | Rate | Pitch | Effect |
|-------------|------|-------|--------|
| Question (`?`) | -15% | +5Hz | Slower, higher pitch (questioning) |
| Exclamation (`!`) | +15% | +10Hz | Faster, higher pitch (excited) |
| Other | +0% | +0Hz | Normal |

## Comparison with Kokoro

| Feature | Kokoro (tts.py) | Edge TTS (tts2.py) |
|---------|-----------------|-------------------|
| Voice quality | Good | Excellent |
| Spanish support | Limited | Multiple regions |
| GPU required | Yes (recommended) | No |
| Offline | Yes | No (requires internet) |
| Speed | Fast | Very fast |
| Custom voices | Yes | No |
| SSML support | Limited | Full |
| Cost | Free | Free |

## When to use each

**Use Kokoro (tts.py) when:**
- You need offline capability
- You want custom voice cloning
- You have a good GPU
- You need specific voice characteristics

**Use Edge TTS (tts2.py) when:**
- You want the most natural voices
- You need regional Spanish accents
- You don't have a GPU
- You want fast generation
- You need fine-grained prosody control

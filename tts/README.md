# Text-to-Speech (TTS)

This module converts text files to speech audio using Microsoft Edge TTS.

## Features

- **Natural voices**: Microsoft's neural voices are highly realistic
- **Multiple Spanish accents**: Spain, Mexico, Chile, Argentina
- **No GPU required**: Works on CPU efficiently
- **Free**: No API keys or costs

## Installation

```bash
pip install -r tts/requirements.txt
```

## Usage

```bash
python tts/tts.py <file_path> [options]
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
python tts/tts.py story/chapter1.txt
```

List available voices:
```bash
python tts/tts.py --list-voices
```

Custom voice:
```bash
python tts/tts.py story/chapter1.txt --voice es-MX-DaliaNeural
```

Custom output directory:
```bash
python tts/tts.py story/chapter1.txt --output-dir chapter1 --voice es-ES-AlvaroNeural
```

## Output

The generated audio file will be saved as `tts/dialog/<filename>.wav` by default.

If you specify `--output-dir`, it will be saved as `tts/dialog/<output-dir>/<filename>.wav`.

For example, running:
```bash
python tts/tts.py story/chapter1.txt --output-dir chapter1
```

Will generate: `tts/dialog/chapter1/chapter1.wav`

## Available Voices

| Voice | Description |
|-------|-------------|
| `es-ES-ElviraNeural` | Female Spanish (Spain) |
| `es-ES-AlvaroNeural` | Male Spanish (Spain) |
| `es-MX-DaliaNeural` | Female Spanish (Mexico) |
| `es-MX-JorgeNeural` | Male Spanish (Mexico) |
| `es-CL-CatalinaNeural` | Female Spanish (Chile) |
| `es-CL-LorenzoNeural` | Male Spanish (Chile) |
| `es-AR-ElenaNeural` | Female Spanish (Argentina) |
| `es-AR-TomasNeural` | Male Spanish (Argentina) |

For a full list, run: `python tts/tts.py --list-voices`

## Custom Pronunciations

You can add custom pronunciations in `tts/pronunciations.yml`. The file already includes common Magic: The Gathering terms.

```yaml
planeswalker: plensuóker
eldrazi: eldrasi
zendikar: sendikár
```

The script automatically handles capitalized versions of words.

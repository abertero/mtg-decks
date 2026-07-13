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

## Ambient Background

Add pleasant ambient sounds as background to your audio files:

```bash
python tts/ambient.py <input_wav> [options]
```

### Options

- `--output-mp3`: Output MP3 file path (default: `<input>_ambient.mp3`)
- `--type`: Background type (default: `rain`)
  - `pink` - Pink noise (soft, like rain)
  - `brown` - Brown noise (very soft, like waterfall)
  - `ocean` - Ocean waves
  - `rain` - Rain sound
  - `pad` - Soft ambient pad
- `--volume`: Background volume percentage (default: 15)

### Examples

Basic usage (rain at 15% volume):
```bash
python tts/ambient.py tts/dialog/chapter1.wav
```

Ocean waves at 20% volume:
```bash
python tts/ambient.py tts/dialog/chapter1.wav --type ocean --volume 20
```

Custom output file:
```bash
python tts/ambient.py tts/dialog/chapter1.wav --type pad --output-mp3 tts/dialog/chapter1_final.mp3
```

### Background Types

| Type | Description | Best For |
|------|-------------|----------|
| `pink` | Soft pink noise | General background |
| `brown` | Very soft brown noise | Deep focus |
| `ocean` | Ocean waves | Relaxing content |
| `rain` | Rain sound | Storytelling, calm content |
| `pad` | Ambient synthesizer pad | Meditative, atmospheric |

## Binaural Background

You can add binaural beats as background to your audio files:

```bash
python tts/binaural.py <input_wav> [options]
```

### Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `input_wav` | Path to input WAV file (required) | - |
| `--output-mp3` | Output MP3 file path | `<input>_binaural.mp3` |
| `--base-freq` | Base frequency in Hz | `200` |
| `--beat-freq` | Beat frequency in Hz | `10` |
| `--volume` | Binaural volume percentage | `20` |

### Examples

Basic usage:
```bash
python tts/binaural.py tts/dialog/chapter1.wav
```

Custom frequencies and volume:
```bash
python tts/binaural.py tts/dialog/chapter1.wav --base-freq 150 --beat-freq 5 --volume 15
```

Custom output file:
```bash
python tts/binaural.py tts/dialog/chapter1.wav --output-mp3 tts/dialog/chapter1_final.mp3
```

### Binaural Beat Effects

Different beat frequencies are associated with different brain states:

| Beat Frequency | Brain Wave | Effect |
|----------------|------------|--------|
| 1-4 Hz | Delta | Deep sleep |
| 4-8 Hz | Theta | Meditation, creativity |
| 8-14 Hz | Alpha | Relaxation, focus |
| 14-30 Hz | Beta | Alertness, concentration |
| 30+ Hz | Gamma | High-level cognitive processing |

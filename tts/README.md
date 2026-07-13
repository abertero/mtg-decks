# Text-to-Speech (TTS)

This module converts text files to speech audio using the Kokoro TTS model.

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
| `--voice` | Voice name to use | `ef_dora` |
| `--speed` | Speech speed (0.1 to 2.0) | `0.9` |

### Examples

Basic usage:
```bash
python tts/tts.py story/chapter1.txt
```

Custom voice and speed:
```bash
python tts/tts.py story/chapter1.txt --voice af_nicole --speed 1.0
```

Custom output directory:
```bash
python tts/tts.py story/chapter1.txt --output-dir chapter1
```

Full example:
```bash
python tts/tts.py story/chapter1.txt --output-dir chapter1 --voice ef_dora --speed 0.9
```

## Output

The generated audio file will be saved as `tts/dialog/<filename>.wav` by default.

If you specify `--output-dir`, it will be saved as `tts/dialog/<output-dir>/<filename>.wav`.

For example, running:
```bash
python tts/tts.py story/chapter1.txt --output-dir chapter1
```

Will generate: `tts/dialog/chapter1/chapter1.wav`

## Custom Pronunciations

You can add custom pronunciations in `tts/pronunciations.yml`. The file already includes common Magic: The Gathering terms.

```yaml
planeswalker: plensuóker
eldrazi: eldrasi
zendikar: sendikár
```

The script automatically handles capitalized versions of words.

## Available Voices

Voices are downloaded automatically on first use and cached in `tts/voices/`. Some available voices:

- `ef_dora` - Female Spanish voice
- `af_nicole` - Female English voice
- `em_santa` - Male English voice

For a full list, check the [Kokoro model repository](https://huggingface.co/hexgrad/Kokoro-82M/tree/main/voices).

## Pause Durations

The script automatically adds pauses for punctuation:

| Punctuation | Duration |
|-------------|----------|
| Newline (`\n`) | 1500ms |
| Ellipsis (`...`) | 800ms |
| Period (`.`) | 600ms |
| Comma (`,`) | 300ms |

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

| Alias | Voice | Description |
|-------|-------|-------------|
| `elvira` | `es-ES-ElviraNeural` | Female Spanish (Spain) |
| `alvaro` | `es-ES-AlvaroNeural` | Male Spanish (Spain) |
| `dalia` | `es-MX-DaliaNeural` | Female Spanish (Mexico) |
| `jorge` | `es-MX-JorgeNeural` | Male Spanish (Mexico) |
| `catalina` | `es-CL-CatalinaNeural` | Female Spanish (Chile) |
| `lorenzo` | `es-CL-LorenzoNeural` | Male Spanish (Chile) |
| `elena` | `es-AR-ElenaNeural` | Female Spanish (Argentina) |
| `tomas` | `es-AR-TomasNeural` | Male Spanish (Argentina) |
| `alex` | `es-PE-AlexNeural` | Male Spanish (Peru) |

For a full list, run: `python tts/tts.py --list-voices`

## Custom Pronunciations

You can add custom pronunciations in `tts/pronunciations.yml`. The file already includes common Magic: The Gathering terms.

```yaml
planeswalker: plensuóker
eldrazi: eldrasi
zendikar: sendikár
```

The script automatically handles capitalized versions of words.

## Voice Tags

You can use special tags in your text to change voice, simulate thoughts, or whispers:

### Change Voice for Dialogues

Use `{alias}...{/alias}` to switch to a different voice. Available aliases: `elvira`, `alvaro`, `dalia`, `jorge`, `catalina`, `lorenzo`, `elena`, `tomas`, `alex`:

```
The narrator speaks normally.
{jorge}"Hello, I'm a different character," said the guard.{/jorge}
The narrator continues speaking.
```

### Thoughts

Use `{thought}...{/thought}` to simulate inner thoughts (slower, lower pitch):

```
She looked at the horizon.
{thought}This changes everything,{/thought} she thought.
```

### Whispers

Use `{whisper}...{/whisper}` to simulate whispering (slower, lower pitch):

```
{whisper}Don't move,{/whisper} he whispered quietly.
```

### God Voice

Use `{god}...{/god}` to simulate a powerful, deep voice (slower, much lower pitch, louder):

```
{god}I am the creator of worlds,{/god} spoke the deity.
```

### Goblin Voice

Use `{goblin}...{/goblin}` to simulate a goblin or imp (faster, higher pitch, sneaky):

```
{goblin}Hehehe! Give me your shiny things!{/goblin} cackled the goblin.
```

### Warlock Voice

Use `{warlock}...{/warlock}` to simulate a warlock or dark sorcerer (slower, very deep, menacing):

```
{warlock}Your soul belongs to me now,{/warlock} whispered the warlock.
```

### Combining Voices with Presets

You can combine any voice alias with any preset using the `{alias+preset}...{/alias+preset}` syntax. This applies the preset effect to the specified voice:

```
{dalia+thought}She pondered the question silently,{/dalia+thought} Dalia thought.
{alvaro+whisper}Be careful,{/alvaro+whisper} Alvaro whispered.
{jorge+god}I am eternal,{/jorge+god} Jorge spoke with divine authority.
{elena+goblin}Hehehe!{/elena+goblin} Elena cackled mischievously.
{alex+warlock}Your soul is mine,{/alex+warlock} Alex intoned darkly.
```

All combinations are valid: any of the 9 voice aliases can be paired with any of the 7 presets.

### Complete Example

```
The old wizard stood before the ancient door.
{thought}At last, the moment has come,{/thought} he thought.
{alvaro}"Open the gate," he commanded.{/alvaro}
The door creaked open slowly.
{whisper}Be careful,{/whisper} warned his apprentice.
```

### Available Voice Tags

| Tag | Effect |
|-----|--------|
| `{elvira}...{/elvira}` | Female Spanish (Spain) |
| `{alvaro}...{/alvaro}` | Male Spanish (Spain) |
| `{dalia}...{/dalia}` | Female Spanish (Mexico) |
| `{jorge}...{/jorge}` | Male Spanish (Mexico) |
| `{catalina}...{/catalina}` | Female Spanish (Chile) |
| `{lorenzo}...{/lorenzo}` | Male Spanish (Chile) |
| `{elena}...{/elena}` | Female Spanish (Argentina) |
| `{tomas}...{/tomas}` | Male Spanish (Argentina) |
| `{alex}...{/alex}` | Male Spanish (Peru) |
| `{thought}...{/thought}` | Slower, lower pitch (thoughts) |
| `{whisper}...{/whisper}` | Slower, lower pitch (whispers) |
| `{god}...{/god}` | Much slower, deeper, louder (deities) |
| `{goblin}...{/goblin}` | Faster, higher pitch, sneaky (goblins/imps) |
| `{warlock}...{/warlock}` | Slower, very deep, menacing (warlocks/sorcerers) |
| `{alias+preset}...{/alias+preset}` | Combine any voice with any preset (e.g., `{dalia+thought}`) |

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
- `--bitrate`: MP3 bitrate (default: `192k`, options: `128k`, `192k`, `256k`, `320k`)

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

High quality for streaming platforms:
```bash
python tts/ambient.py tts/dialog/chapter1.wav --bitrate 320k
```

### Background Types

| Type | Description | Best For |
|------|-------------|----------|
| `pink` | Soft pink noise | General background |
| `brown` | Very soft brown noise | Deep focus |
| `ocean` | Ocean waves | Relaxing content |
| `rain` | Rain sound | Storytelling, calm content |
| `pad` | Ambient synthesizer pad | Meditative, atmospheric |

## Concatenate Audio Files

Combine multiple audio files with silence between them:

```bash
python tts/concat.py <input1> <input2> [...] [options]
```

### Options

- `--output`, `-o`: Output MP3 file (default: `output.mp3`)
- `--silence`, `-s`: Silence duration in milliseconds (default: 2000)
- `--bitrate`: MP3 bitrate (default: `192k`, options: `128k`, `192k`, `256k`, `320k`)

### Examples

Concatenate two files with 2 seconds of silence:
```bash
python tts/concat.py tts/dialog/chapter1.mp3 tts/dialog/chapter2.mp3 -o tts/dialog/full_story.mp3
```

Concatenate three files with 5 seconds of silence:
```bash
python tts/concat.py intro.mp3 main.mp3 outro.mp3 --silence 5000 -o tts/dialog/complete.mp3
```

Concatenate multiple chapter files:
```bash
python tts/concat.py tts/dialog/chapter*.mp3 -o tts/dialog/full_book.mp3
```

High quality for streaming platforms:
```bash
python tts/concat.py tts/dialog/chapter1.mp3 tts/dialog/chapter2.mp3 --bitrate 320k -o tts/dialog/final.mp3
```

### Notes

- Supports both `.wav` and `.mp3` input files
- Output is always MP3 format
- Files are concatenated in the order provided

## Audio Quality & Bitrates

Both `ambient.py` and `concat.py` support custom bitrates for MP3 output. The default is **192 kbps**, which is suitable for most use cases.

### Recommended Bitrates

| Bitrate | Quality | Use Case |
|---------|---------|----------|
| `128k` | Good | Web streaming, podcasts |
| `192k` | Very Good | General purpose (default) |
| `256k` | Excellent | High quality audio |
| `320k` | Maximum | Professional, Spotify, Apple Music |

### Platform Requirements

- **Spotify**: 160-320 kbps (OGG Vorbis for streaming, accepts high-quality MP3)
- **Apple Music**: 256 kbps AAC
- **YouTube**: 128-192 kbps AAC
- **Professional/Archival**: 320 kbps CBR

### Examples

For Spotify or professional distribution:
```bash
python tts/ambient.py input.wav --bitrate 320k
python tts/concat.py file1.mp3 file2.mp3 --bitrate 320k -o output.mp3
```

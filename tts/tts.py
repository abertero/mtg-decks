import edge_tts
import asyncio
import os
import sys
import re
import yaml
import argparse
import tempfile
from pydub import AudioSegment

EDGE_VOICES = {
    'es-ES-ElviraNeural': 'Female Spanish (Spain)',
    'es-ES-AlvaroNeural': 'Male Spanish (Spain)',
    'es-MX-DaliaNeural': 'Female Spanish (Mexico)',
    'es-MX-JorgeNeural': 'Male Spanish (Mexico)',
    'es-CL-CatalinaNeural': 'Female Spanish (Chile)',
    'es-CL-LorenzoNeural': 'Male Spanish (Chile)',
    'es-AR-ElenaNeural': 'Female Spanish (Argentina)',
    'es-AR-TomasNeural': 'Male Spanish (Argentina)',
    'es-PE-AlexNeural': 'Male Spanish (Peru)'
}

VOICE_PRESETS = {
    'thought': {'rate': '-10%', 'pitch': '-5Hz'},
    'whisper': {'rate': '-20%', 'pitch': '-10Hz'},
    'god': {'rate': '-15%', 'pitch': '-20Hz', 'volume': '+10%'},
    'child': {'rate': '+10%', 'pitch': '+8Hz'},
    'old': {'rate': '-15%', 'pitch': '-10Hz'},
}


def load_pronunciations(pronunciations_file):
    if not os.path.exists(pronunciations_file):
        return {}
    with open(pronunciations_file, 'r', encoding='utf-8') as f:
        raw_dict = yaml.safe_load(f) or {}
    pronunciation_dict = {}
    for word, pronunciation in raw_dict.items():
        pronunciation_dict[word] = pronunciation
        capitalized = word.capitalize()
        if capitalized != word:
            pronunciation_dict[capitalized] = pronunciation
    return pronunciation_dict


def apply_pronunciations(text, pronunciation_dict):
    for word, pronunciation in pronunciation_dict.items():
        text = re.sub(r'\b' + re.escape(word) + r'\b', pronunciation, text)
    return text


PAUSE_SEPARATOR = '\x00'
PAUSE_DURATION_MS = 400


def normalize_pauses(text):
    text = re.sub(r'\.{3,}', ', ', text)
    text = text.replace('…', ', ')
    text = text.replace(';', PAUSE_SEPARATOR)
    text = text.replace(':', PAUSE_SEPARATOR)
    return text


def is_pronounceable(text):
    cleaned = re.sub(r'[―—\-\s\.\,\;\:\!\?\"\'\(\)\[\]\{\}…·]', '', text)
    return len(cleaned) > 0


def parse_voice_tags(text, default_voice):
    """Parse voice tags and return list of (text, voice, rate, pitch, volume) segments"""
    segments = []
    pattern = r'\{(voice:([^}]+)|thought|whisper|god|child|old)\}(.*?)\{/(voice|thought|whisper|god|child|old)\}'
    
    last_end = 0
    for match in re.finditer(pattern, text, re.DOTALL):
        if match.start() > last_end:
            before_text = text[last_end:match.start()].strip()
            if before_text and is_pronounceable(before_text):
                segments.append((before_text, default_voice, '+0%', '+0Hz', '+0%'))
        
        tag_type = match.group(1)
        content = match.group(3).strip()
        
        if tag_type.startswith('voice:'):
            voice = match.group(2)
            if content and is_pronounceable(content):
                segments.append((content, voice, '+0%', '+0Hz', '+0%'))
        elif tag_type in VOICE_PRESETS:
            preset = VOICE_PRESETS[tag_type]
            if content and is_pronounceable(content):
                segments.append((content, default_voice, preset.get('rate', '+0%'), preset.get('pitch', '+0Hz'), preset.get('volume', '+0%')))
        
        last_end = match.end()
    
    if last_end < len(text):
        remaining = text[last_end:].strip()
        if remaining and is_pronounceable(remaining):
            segments.append((remaining, default_voice, '+0%', '+0Hz', '+0%'))
    
    return segments


async def synthesize_segment(text, voice, rate, pitch, volume, output_path):
    """Synthesize a single segment with specific parameters"""
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, volume=volume)
    await communicate.save(output_path)


async def synthesize_speech(segments, output_path):
    """Synthesize multiple segments and concatenate them"""
    if len(segments) == 1:
        text, voice, rate, pitch, volume = segments[0]
        if not text.strip():
            silence = AudioSegment.silent(duration=PAUSE_DURATION_MS)
            silence.export(output_path, format='wav')
        else:
            communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, volume=volume)
            await communicate.save(output_path)
        return
    
    with tempfile.TemporaryDirectory() as temp_dir:
        audio_files = []
        for i, (text, voice, rate, pitch, volume) in enumerate(segments):
            if not text.strip():
                silence = AudioSegment.silent(duration=PAUSE_DURATION_MS)
                temp_path = os.path.join(temp_dir, f'segment_{i}.wav')
                silence.export(temp_path, format='wav')
            else:
                temp_path = os.path.join(temp_dir, f'segment_{i}.mp3')
                await synthesize_segment(text, voice, rate, pitch, volume, temp_path)
            audio_files.append(temp_path)
        
        # Concatenate all segments
        first = audio_files[0]
        combined = AudioSegment.from_wav(first) if first.endswith('.wav') else AudioSegment.from_mp3(first)
        for audio_file in audio_files[1:]:
            segment = AudioSegment.from_wav(audio_file) if audio_file.endswith('.wav') else AudioSegment.from_mp3(audio_file)
            combined += segment
        
        combined.export(output_path, format='wav')


async def tts(file_path, output_dir, voice='es-ES-ElviraNeural'):
    script_dir = os.path.dirname(os.path.abspath(__file__))

    pronunciations_file = os.path.join(script_dir, 'pronunciations.yml')
    pronunciation_dict = load_pronunciations(pronunciations_file)

    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    text = apply_pronunciations(text, pronunciation_dict)
    text = normalize_pauses(text)

    segments = parse_voice_tags(text, voice)

    expanded_segments = []
    for seg_text, seg_voice, seg_rate, seg_pitch, seg_volume in segments:
        parts = seg_text.split(PAUSE_SEPARATOR)
        for j, part in enumerate(parts):
            part = part.strip()
            if part and is_pronounceable(part):
                expanded_segments.append((part, seg_voice, seg_rate, seg_pitch, seg_volume))
            if j < len(parts) - 1:
                expanded_segments.append(('', seg_voice, seg_rate, seg_pitch, seg_volume))

    while expanded_segments and not expanded_segments[0][0].strip():
        expanded_segments.pop(0)
    while expanded_segments and not expanded_segments[-1][0].strip():
        expanded_segments.pop()

    if not expanded_segments:
        expanded_segments = segments

    dialog_dir = os.path.join(script_dir, 'dialog')
    if output_dir:
        out_dir = os.path.join(dialog_dir, output_dir)
    else:
        out_dir = dialog_dir

    os.makedirs(out_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_path = os.path.join(out_dir, f'{base_name}.wav')

    print(f'Generando audio con Edge TTS ({len(expanded_segments)} segmento(s))...')
    await synthesize_speech(expanded_segments, output_path)
    print(f'Archivo guardado: {output_path}')
    return output_path


def parse_args():
    parser = argparse.ArgumentParser(description='Text-to-Speech converter (Edge TTS)')
    parser.add_argument('file_path', help='Path to the input text file')
    parser.add_argument('--output-dir', default=None, help='Output subdirectory inside dialog folder (default: dialog/)')
    parser.add_argument('--voice', default='es-ES-ElviraNeural', help='Voice name to use (default: es-ES-ElviraNeural)')
    parser.add_argument('--list-voices', action='store_true', help='List available Spanish voices')
    return parser.parse_args()


async def main():
    args = parse_args()

    if args.list_voices:
        print('Available Spanish voices:')
        for voice, description in EDGE_VOICES.items():
            print(f'  {voice}: {description}')
        return

    if not os.path.exists(args.file_path):
        print(f"Error: No se encontró el archivo '{args.file_path}'")
        sys.exit(1)

    await tts(args.file_path, args.output_dir, args.voice)


if __name__ == '__main__':
    asyncio.run(main())

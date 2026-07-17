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

VOICE_ALIASES = {
    alias: full_name
    for full_name in EDGE_VOICES
    for alias in [full_name.split('-')[-1].replace('Neural', '').lower()]
}

VOICE_PRESETS = {
    'thought': {'rate': '-10%', 'pitch': '-5Hz'},
    'whisper': {'rate': '-20%', 'pitch': '-10Hz'},
    'god': {'rate': '-15%', 'pitch': '-20Hz', 'volume': '+10%'},
    'child': {'rate': '+10%', 'pitch': '+8Hz'},
    'old': {'rate': '-15%', 'pitch': '-10Hz'},
    'goblin': {'rate': '+20%', 'pitch': '+12Hz', 'volume': '-5%'},
    'warlock': {'rate': '-20%', 'pitch': '-25Hz', 'volume': '+5%'},
}

ALL_TAGS = set(VOICE_ALIASES.keys()) | set(VOICE_PRESETS.keys())


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
        if ' ' in word or not re.match(r'^\w+$', word):
            text = re.sub(re.escape(word), pronunciation, text, flags=re.IGNORECASE)
        else:
            text = re.sub(r'\b' + re.escape(word) + r'\b', pronunciation, text)
    return text


def normalize_pauses(text):
    text = re.sub(r'\.{3,}', ', ', text)
    text = text.replace('…', '. ')
    text = text.replace(';', ',')
    text = re.sub(r':(?![^{}]*\})', ',', text)
    return text


def is_pronounceable(text):
    cleaned = re.sub(r'[―—\-\s\.\,\;\:\!\?\"\'\(\)\[\]\{\}…·]', '', text)
    return len(cleaned) > 0


def validate_voice_tags(text):
    """Validate that all voice tags are properly closed"""
    tags_pattern = '|'.join(re.escape(t) for t in ALL_TAGS)
    open_pattern = rf'\{{({tags_pattern})\}}'
    close_pattern = rf'\{{/({tags_pattern})\}}'
    
    opens = list(re.finditer(open_pattern, text))
    closes = list(re.finditer(close_pattern, text))
    
    if len(opens) != len(closes):
        first_unmatched = opens[-1] if len(opens) > len(closes) else closes[-1]
        line_num = text[:first_unmatched.start()].count('\n') + 1
        line_content = text.split('\n')[line_num - 1].strip()
        tag = first_unmatched.group(0)
        kind = "apertura" if len(opens) > len(closes) else "cierre"
        raise ValueError(
            f"Mismatch de tags: {len(opens)} apertura(s) vs {len(closes)} cierre(s)\n"
            f"  Línea {line_num}: {line_content}\n"
            f"  Tag sin par: {tag} ({kind})"
        )
    
    stack = []
    all_tags = []
    for m in opens:
        all_tags.append(('open', m.group(1), m.start(), m.group(0)))
    for m in closes:
        all_tags.append(('close', m.group(1), m.start(), m.group(0)))
    all_tags.sort(key=lambda x: x[2])
    
    for tag_type, tag_name, pos, tag_raw in all_tags:
        line_num = text[:pos].count('\n') + 1
        line_content = text.split('\n')[line_num - 1].strip()
        
        if tag_type == 'open':
            stack.append((tag_name, line_num, line_content, tag_raw))
        else:
            if not stack:
                raise ValueError(
                    f"Tag de cierre '{tag_raw}' sin apertura\n"
                    f"  Línea {line_num}: {line_content}"
                )
            expected, exp_line, exp_content, exp_raw = stack.pop()
            if expected != tag_name:
                raise ValueError(
                    f"Tag '{tag_raw}' no coincide con '{exp_raw}'\n"
                    f"  Apertura en línea {exp_line}: {exp_content}\n"
                    f"  Cierre en línea {line_num}: {line_content}"
                )
    
    if stack:
        errors = []
        for tag_name, line_num, line_content, tag_raw in stack:
            errors.append(f"  Línea {line_num}: {line_content}\n    Tag sin cerrar: {tag_raw}")
        raise ValueError("Tag(s) sin cerrar:\n" + "\n".join(errors))


def parse_voice_tags(text, default_voice):
    """Parse voice tags and return list of (text, voice, rate, pitch, volume) segments"""
    segments = []
    tags_pattern = '|'.join(re.escape(t) for t in ALL_TAGS)
    pattern = rf'\{{({tags_pattern})\}}(.*?)\{{/({tags_pattern})\}}'
    
    last_end = 0
    for match in re.finditer(pattern, text, re.DOTALL):
        if match.start() > last_end:
            before_text = text[last_end:match.start()].strip()
            if before_text and is_pronounceable(before_text):
                segments.append((before_text, default_voice, '+0%', '+0Hz', '+0%'))
        
        tag_type = match.group(1)
        content = match.group(2).strip()
        
        if tag_type in VOICE_ALIASES:
            voice = VOICE_ALIASES[tag_type]
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
        communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, volume=volume)
        await communicate.save(output_path)
        return
    
    with tempfile.TemporaryDirectory() as temp_dir:
        audio_files = []
        for i, (text, voice, rate, pitch, volume) in enumerate(segments):
            temp_path = os.path.join(temp_dir, f'segment_{i}.mp3')
            await synthesize_segment(text, voice, rate, pitch, volume, temp_path)
            audio_files.append(temp_path)
        
        # Concatenate all segments
        combined = AudioSegment.from_mp3(audio_files[0])
        for audio_file in audio_files[1:]:
            segment = AudioSegment.from_mp3(audio_file)
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
    
    try:
        validate_voice_tags(text)
    except ValueError as e:
        print(f"Error de validación en tags de voz: {e}")
        sys.exit(1)

    segments = parse_voice_tags(text, voice)

    dialog_dir = os.path.join(script_dir, 'dialog')
    if output_dir:
        out_dir = os.path.join(dialog_dir, output_dir)
    else:
        out_dir = dialog_dir

    os.makedirs(out_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_path = os.path.join(out_dir, f'{base_name}.wav')

    print(f'Generando audio con Edge TTS ({len(segments)} segmento(s))...')
    await synthesize_speech(segments, output_path)
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

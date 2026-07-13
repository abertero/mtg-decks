import edge_tts
import asyncio
import os
import sys
import re
import yaml
import argparse
import numpy as np
import soundfile as sf
from pydub import AudioSegment
import tempfile

REPO_ID = 'edge-tts'

SAMPLE_RATE = 24000

PAUSE_DURATIONS = {
    'newline': 1000,
    'ellipsis': 800,
    'period': 600,
    'question': 400,
    'exclamation': 300,
    'comma': 200,
}

RATE_MODIFIERS = {
    'question': '-15%',
    'exclamation': '+15%',
    'default': '+0%',
}

PITCH_MODIFIERS = {
    'question': '+5Hz',
    'exclamation': '+10Hz',
    'default': '+0Hz',
}

EDGE_VOICES = {
    'es-ES-ElviraNeural': 'Female Spanish (Spain)',
    'es-ES-AlvaroNeural': 'Male Spanish (Spain)',
    'es-MX-DaliaNeural': 'Female Spanish (Mexico)',
    'es-MX-JorgeNeural': 'Male Spanish (Mexico)',
    'es-AR-ElenaNeural': 'Female Spanish (Argentina)',
    'es-AR-TomasNeural': 'Male Spanish (Argentina)',
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


def parse_text_parts(text):
    parts = re.split(r'(\n+|\.{3}|\.|\?|!|,)', text)
    result = []
    for part in parts:
        if not part:
            continue
        if '\n' in part and all(c == '\n' for c in part):
            result.append(('newline', len(part)))
        elif part == '...':
            result.append(('ellipsis', 1))
        elif part == '.':
            result.append(('period', 1))
        elif part == '?':
            result.append(('question', 1))
        elif part == '!':
            result.append(('exclamation', 1))
        elif part == ',':
            result.append(('comma', 1))
        else:
            text_part = part.strip()
            if text_part:
                result.append(('text', text_part))
    return result


def create_silence(duration_ms):
    samples = int(SAMPLE_RATE * duration_ms / 1000)
    return np.zeros(samples, dtype=np.float32)


async def synthesize_segment(text, voice, rate, pitch, temp_path):
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await communicate.save(temp_path)
    audio = AudioSegment.from_mp3(temp_path)
    return audio


async def synthesize_speech(text_parts, voice, output_path):
    audio_segments = []
    
    with tempfile.TemporaryDirectory() as temp_dir:
        for i, (part_type, value) in enumerate(text_parts):
            if part_type == 'text':
                next_type = text_parts[i + 1][0] if i + 1 < len(text_parts) else None
                
                if next_type == 'question':
                    rate = RATE_MODIFIERS['question']
                    pitch = PITCH_MODIFIERS['question']
                elif next_type == 'exclamation':
                    rate = RATE_MODIFIERS['exclamation']
                    pitch = PITCH_MODIFIERS['exclamation']
                else:
                    rate = RATE_MODIFIERS['default']
                    pitch = PITCH_MODIFIERS['default']
                
                temp_path = os.path.join(temp_dir, f'segment_{i}.mp3')
                audio = await synthesize_segment(value, voice, rate, pitch, temp_path)
                audio_segments.append(audio)
            elif part_type in PAUSE_DURATIONS:
                silence = AudioSegment.silent(duration=PAUSE_DURATIONS[part_type])
                audio_segments.append(silence)
    
    if audio_segments:
        combined = audio_segments[0]
        for segment in audio_segments[1:]:
            combined += segment
        combined.export(output_path, format='wav')


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
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    pronunciations_file = os.path.join(script_dir, 'pronunciations.yml')
    pronunciation_dict = load_pronunciations(pronunciations_file)
    
    with open(args.file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    text = apply_pronunciations(text, pronunciation_dict)
    
    text_parts = parse_text_parts(text)
    
    dialog_dir = os.path.join(script_dir, 'dialog')
    if args.output_dir:
        output_dir = os.path.join(dialog_dir, args.output_dir)
    else:
        output_dir = dialog_dir
    
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(args.file_path))[0]
    output_path = os.path.join(output_dir, f'{base_name}.wav')
    
    print(f'Generando audio con Edge TTS...')
    await synthesize_speech(text_parts, args.voice, output_path)
    print(f'Archivo guardado: {output_path}')


if __name__ == '__main__':
    asyncio.run(main())

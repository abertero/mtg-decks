from kokoro import KPipeline
from IPython.display import display, Audio
from huggingface_hub import hf_hub_download
import numpy as np
import soundfile as sf
import os
import sys
import shutil
import re
import yaml
import argparse

SAMPLE_RATE = 24000
REPO_ID = 'hexgrad/Kokoro-82M'

PAUSE_DURATIONS = {
    'newline': 1000,
    'ellipsis': 800,
    'period': 600,
    'comma': 200,
}


def load_voice(voice_name, voices_dir):
    voice_file = os.path.join(voices_dir, f'{voice_name}.pt')
    if not os.path.exists(voice_file):
        print(f'Descargando voz {voice_name}...')
        downloaded = hf_hub_download(repo_id=REPO_ID, filename=f'voices/{voice_name}.pt')
        shutil.copy(downloaded, voice_file)
        print(f'Voz guardada en {voice_file}')
    return voice_file


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
    parts = re.split(r'(\n+|\.{3}|\.|,)', text)
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
        elif part == ',':
            result.append(('comma', 1))
        else:
            text_part = part.strip()
            if text_part:
                result.append(('text', text_part))
    return result


def generate_audio_segments(text_parts, pipeline, voice_file, speed):
    audio_segments = []
    sequence = []
    for part_type, value in text_parts:
        if part_type == 'text':
            generator = pipeline(value, voice=voice_file, speed=speed, split_pattern=None)
            for gs, ps, audio in generator:
                print(gs, ps)
                audio_segments.append(audio)
                sequence.append(('audio', None))
        else:
            sequence.append((part_type, value))
    return audio_segments, sequence


def create_silence(duration_ms):
    samples = int(SAMPLE_RATE * duration_ms / 1000)
    return np.zeros(samples, dtype=np.float32)


def combine_audio_with_pauses(audio_segments, sequence):
    silences = {key: create_silence(ms) for key, ms in PAUSE_DURATIONS.items()}
    audio_with_pauses = []
    audio_index = 0
    for pause_type, count in sequence:
        if pause_type == 'audio':
            if audio_index < len(audio_segments):
                audio_with_pauses.append(audio_segments[audio_index])
                audio_index += 1
        elif pause_type in silences:
            for _ in range(count):
                audio_with_pauses.append(silences[pause_type])
    return np.concatenate(audio_with_pauses) if audio_with_pauses else None


def save_audio(audio, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    sf.write(output_path, audio, SAMPLE_RATE)
    display(Audio(data=audio, rate=SAMPLE_RATE, autoplay=True))
    print(f'Archivo guardado: {output_path}')


def parse_args():
    parser = argparse.ArgumentParser(description='Text-to-Speech converter')
    parser.add_argument('file_path', help='Path to the input text file')
    parser.add_argument('--output-dir', default=None, help='Output subdirectory inside dialog folder (default: dialog/)')
    parser.add_argument('--voice', default='ef_dora', help='Voice name to use (default: ef_dora)')
    parser.add_argument('--speed', type=float, default=0.9, help='Speech speed from 0.1 to 2.0 (default: 0.9)')
    return parser.parse_args()


def main():
    args = parse_args()

    if not os.path.exists(args.file_path):
        print(f"Error: No se encontró el archivo '{args.file_path}'")
        sys.exit(1)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    voices_dir = os.path.join(script_dir, 'voices')
    os.makedirs(voices_dir, exist_ok=True)

    voice_file = load_voice(args.voice, voices_dir)

    pronunciations_file = os.path.join(script_dir, 'pronunciations.yml')
    pronunciation_dict = load_pronunciations(pronunciations_file)

    with open(args.file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    text = apply_pronunciations(text, pronunciation_dict)

    pipeline = KPipeline(lang_code='e')
    text_parts = parse_text_parts(text)
    audio_segments, sequence = generate_audio_segments(text_parts, pipeline, voice_file, args.speed)

    if audio_segments:
        combined = combine_audio_with_pauses(audio_segments, sequence)
        if combined is not None:
            dialog_dir = os.path.join(script_dir, 'dialog')
            if args.output_dir:
                output_dir = os.path.join(dialog_dir, args.output_dir)
            else:
                output_dir = dialog_dir
            base_name = os.path.splitext(os.path.basename(args.file_path))[0]
            wav_path = os.path.join(output_dir, f'{base_name}.wav')
            save_audio(combined, wav_path)


if __name__ == '__main__':
    main()

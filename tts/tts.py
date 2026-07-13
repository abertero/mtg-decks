import edge_tts
import asyncio
import os
import sys
import re
import yaml
import argparse

EDGE_VOICES = {
    'es-ES-ElviraNeural': 'Female Spanish (Spain)',
    'es-ES-AlvaroNeural': 'Male Spanish (Spain)',
    'es-MX-DaliaNeural': 'Female Spanish (Mexico)',
    'es-MX-JorgeNeural': 'Male Spanish (Mexico)',
    'es-CL-CatalinaNeural': 'Female Spanish (Chile)',
    'es-CL-LorenzoNeural': 'Male Spanish (Chile)',
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


async def synthesize_speech(text, voice, output_path):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)


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
    
    dialog_dir = os.path.join(script_dir, 'dialog')
    if args.output_dir:
        output_dir = os.path.join(dialog_dir, args.output_dir)
    else:
        output_dir = dialog_dir
    
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(args.file_path))[0]
    output_path = os.path.join(output_dir, f'{base_name}.wav')
    
    print(f'Generando audio con Edge TTS...')
    await synthesize_speech(text, args.voice, output_path)
    print(f'Archivo guardado: {output_path}')


if __name__ == '__main__':
    asyncio.run(main())

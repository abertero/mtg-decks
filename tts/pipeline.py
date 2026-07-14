import asyncio
import json
import os
import sys

from tts import tts
from ambient import ambient
from concat import concat


def load_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


async def run_pipeline(config_path):
    config = load_config(config_path)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    dialog_dir = os.path.join(script_dir, 'dialog')
    output_dir = config.get('output_dir', '')

    if output_dir:
        out_dir_full = os.path.join(dialog_dir, output_dir)
    else:
        out_dir_full = dialog_dir
    os.makedirs(out_dir_full, exist_ok=True)

    generated_files = []

    for i, segment in enumerate(config.get('segments', [])):
        text_path = os.path.join(script_dir, segment['text'])
        ambient_config = segment.get('ambient', None)
        base_name = os.path.splitext(os.path.basename(text_path))[0]

        if not segment.get('process', False):
            if ambient_config:
                existing_path = os.path.join(out_dir_full, f'{base_name}.mp3')
            else:
                existing_path = os.path.join(out_dir_full, f'{base_name}.wav')
            if os.path.exists(existing_path):
                print(f'\n--- Segmento {i + 1}: {os.path.basename(text_path)} (omitido, usando existente) ---')
                generated_files.append(existing_path)
            else:
                print(f'\n--- Segmento {i + 1}: {os.path.basename(text_path)} (omitido, archivo no encontrado: {existing_path}) ---')
            continue

        voice = segment.get('voice', 'es-ES-ElviraNeural')

        print(f'\n--- Segmento {i + 1}: {os.path.basename(text_path)} ---')

        wav_path = await tts(text_path, output_dir, voice)

        if ambient_config and wav_path:
            ambient_type = ambient_config.get('type', 'rain')
            ambient_volume = ambient_config.get('volume', 60)
            mp3_path = os.path.join(out_dir_full, f'{base_name}.mp3')
            ambient(wav_path, ambient_type, ambient_volume, mp3_path)
            generated_files.append(mp3_path)
        elif wav_path:
            generated_files.append(wav_path)

    extra_files = []
    for ef in config.get('extra_files', []):
        extra_files.append(os.path.join(script_dir, ef))

    all_files = generated_files + extra_files

    output_file = config.get('output_file', 'output.mp3')
    output_path = os.path.join(out_dir_full, output_file)

    print(f'\n--- Concatenando {len(all_files)} archivos ---')
    concat(all_files, output_path)

    print(f'\n✓ Pipeline completado: {output_path}')


def main():
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        print(f"Error: Falta archivo de configuración")
        sys.exit(1)

    if not os.path.exists(config_path):
        print(f"Error: No se encontró el archivo de configuración '{config_path}'")
        sys.exit(1)

    asyncio.run(run_pipeline(config_path))


if __name__ == '__main__':
    main()

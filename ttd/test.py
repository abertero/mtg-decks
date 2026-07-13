from kokoro import KPipeline
from IPython.display import display, Audio
from huggingface_hub import hf_hub_download
import numpy as np
import soundfile as sf
import os
import sys
import shutil

if len(sys.argv) < 2:
    print("Uso: python test.py <ruta_al_archivo.txt>")
    sys.exit(1)

file_path = sys.argv[1]
if not os.path.exists(file_path):
    print(f"Error: No se encontró el archivo '{file_path}'")
    sys.exit(1)

script_dir = os.path.dirname(os.path.abspath(__file__))
voices_dir = os.path.join(script_dir, 'voices')
os.makedirs(voices_dir, exist_ok=True)

voice_name = 'if_sara'
voice_file = os.path.join(voices_dir, f'{voice_name}.pt')
if not os.path.exists(voice_file):
    print(f'Descargando voz {voice_name}...')
    downloaded = hf_hub_download(repo_id='hexgrad/Kokoro-82M', filename=f'voices/{voice_name}.pt')
    shutil.copy(downloaded, voice_file)
    print(f'Voz guardada en {voice_file}')

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

pipeline = KPipeline(lang_code='e')
pause_duration_ms = 1500
generator = pipeline(text, voice=voice_file, speed=0.8, split_pattern=r'\n+')

all_audio = []
for i, (gs, ps, audio) in enumerate(generator):
    print(i, gs, ps)
    all_audio.append(audio)

if all_audio:
    sample_rate = 24000
    silence_samples = int(sample_rate * pause_duration_ms / 1000)
    silence = np.zeros(silence_samples, dtype=np.float32)
    
    audio_with_pauses = []
    for i, audio in enumerate(all_audio):
        audio_with_pauses.append(audio)
        if i < len(all_audio) - 1:
            audio_with_pauses.append(silence)
    
    combined = np.concatenate(audio_with_pauses)
    
    dialog_dir = os.path.join(script_dir, 'dialog')
    os.makedirs(dialog_dir, exist_ok=True)
    
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    wav_path = os.path.join(dialog_dir, f'{base_name}.wav')
    
    sf.write(wav_path, combined, 24000)
    display(Audio(data=combined, rate=24000, autoplay=True))
    print(f'Archivo guardado: {wav_path}')
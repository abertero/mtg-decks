from kokoro import KPipeline
from IPython.display import display, Audio
import numpy as np
import soundfile as sf
import os
import sys

if len(sys.argv) < 2:
    print("Uso: python test.py <ruta_al_archivo.txt>")
    sys.exit(1)

file_path = sys.argv[1]
if not os.path.exists(file_path):
    print(f"Error: No se encontró el archivo '{file_path}'")
    sys.exit(1)

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

pipeline = KPipeline(lang_code='e')
voice = 'ef_dora'
generator = pipeline(text, voice=voice, speed=1, split_pattern=r'\n+')

all_audio = []
for i, (gs, ps, audio) in enumerate(generator):
    print(i, gs, ps)
    all_audio.append(audio)

if all_audio:
    combined = np.concatenate(all_audio)
    wav_path = 'voice\\output.wav'
    sf.write(wav_path, combined, 24000)
    display(Audio(data=combined, rate=24000, autoplay=True))
    print(f'Archivo guardado: {wav_path}')
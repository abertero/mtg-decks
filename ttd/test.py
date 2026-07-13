from kokoro import KPipeline
from IPython.display import display, Audio
from pydub import AudioSegment
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

for i, (gs, ps, audio) in enumerate(generator):
    print(i, gs, ps)
    display(Audio(data=audio, rate=24000, autoplay=i==0))
    wav_path = f'voice\output_{i}.wav'
    sf.write(wav_path, audio, 24000)
    audio_seg = AudioSegment.from_wav(wav_path)
    print(f'Archivo guardado: {wav_path}')
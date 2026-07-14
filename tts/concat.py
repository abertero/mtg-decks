import os
import sys
import argparse
from pydub import AudioSegment
import soundfile as sf
import numpy as np


def load_audio(file_path):
    """Load audio file, handling both WAV and MP3 formats"""
    try:
        # Try pydub first
        if file_path.lower().endswith('.mp3'):
            return AudioSegment.from_mp3(file_path)
        else:
            return AudioSegment.from_wav(file_path)
    except Exception:
        # Fallback to soundfile for problematic WAV files
        audio_data, sample_rate = sf.read(file_path)
        
        # Convert to stereo if mono
        if len(audio_data.shape) == 1:
            audio_data = np.column_stack((audio_data, audio_data))
        
        # Convert to int16
        audio_data_int16 = (audio_data * 32767).astype(np.int16)
        
        return AudioSegment(
            audio_data_int16.tobytes(),
            frame_rate=sample_rate,
            sample_width=2,
            channels=audio_data.shape[1]
        )


def concatenate_with_silence(file_paths, silence_duration_ms=2000):
    """Concatenate multiple audio files with silence between them"""
    if not file_paths:
        return None
    
    # Create silence segment
    silence = AudioSegment.silent(duration=silence_duration_ms)
    
    # Load first file
    combined = load_audio(file_paths[0])
    print(f'  ✓ {file_paths[0]} ({len(combined)/1000:.1f}s)')
    
    # Add remaining files with silence
    for file_path in file_paths[1:]:
        combined += silence
        audio = load_audio(file_path)
        combined += audio
        print(f'  ✓ {file_path} ({len(audio)/1000:.1f}s)')
    
    return combined


def parse_args():
    parser = argparse.ArgumentParser(description='Concatenate audio files with silence between them')
    parser.add_argument('input_files', nargs='+', help='Input audio files (.wav or .mp3)')
    parser.add_argument('--output', '-o', default='output.mp3', help='Output MP3 file (default: output.mp3)')
    parser.add_argument('--silence', '-s', type=int, default=2000, help='Silence duration in milliseconds (default: 2000)')
    parser.add_argument('--bitrate', default='320k', help='MP3 bitrate (default: 320k, options: 128k, 192k, 256k, 320k)')
    return parser.parse_args()


def main():
    args = parse_args()
    
    # Validate input files
    for file_path in args.input_files:
        if not os.path.exists(file_path):
            print(f"Error: No se encontró el archivo '{file_path}'")
            sys.exit(1)
    
    print(f'Concatenando {len(args.input_files)} archivos con {args.silence}ms de silencio entre pistas...')
    
    combined = concatenate_with_silence(args.input_files, args.silence)
    
    total_duration = len(combined) / 1000
    print(f'\nDuración total: {total_duration:.1f}s')
    
    print(f'Exportando a MP3 ({args.bitrate})...')
    combined.export(args.output, format='mp3', bitrate=args.bitrate)
    print(f'✓ Archivo guardado: {args.output}')


if __name__ == '__main__':
    main()

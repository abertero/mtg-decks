import numpy as np
import os
import sys
import argparse
from pydub import AudioSegment
import soundfile as sf


def generate_pink_noise(duration_ms, sample_rate=44100):
    """Generate pink noise (softer than white noise, like rain)"""
    duration_s = duration_ms / 1000.0
    num_samples = int(sample_rate * duration_s)
    
    white_noise = np.random.normal(0, 1, num_samples)
    
    # Apply pink noise filter
    b = np.array([0.049922035, -0.095993537, 0.050612699, -0.004709510])
    a = np.array([1, -2.494956002, 2.017265875, -0.522189400])
    
    from scipy import signal
    pink_noise = signal.lfilter(b, a, white_noise)
    
    # Normalize
    pink_noise = pink_noise / np.max(np.abs(pink_noise))
    
    # Convert to stereo (same in both channels)
    stereo_noise = np.column_stack((pink_noise, pink_noise))
    stereo_noise = (stereo_noise * 32767).astype(np.int16)
    
    return stereo_noise, sample_rate


def generate_brown_noise(duration_ms, sample_rate=44100):
    """Generate brown noise (very soft, like waterfall)"""
    duration_s = duration_ms / 1000.0
    num_samples = int(sample_rate * duration_s)
    
    white_noise = np.random.normal(0, 1, num_samples)
    brown_noise = np.cumsum(white_noise)
    
    # Normalize
    brown_noise = brown_noise / np.max(np.abs(brown_noise))
    
    # Convert to stereo
    stereo_noise = np.column_stack((brown_noise, brown_noise))
    stereo_noise = (stereo_noise * 32767).astype(np.int16)
    
    return stereo_noise, sample_rate


def generate_ocean_waves(duration_ms, sample_rate=44100):
    """Generate ocean waves sound"""
    duration_s = duration_ms / 1000.0
    t = np.linspace(0, duration_s, int(sample_rate * duration_s), False)
    
    # Base noise
    noise = np.random.normal(0, 1, len(t))
    
    # Apply low-pass filter effect with amplitude modulation
    wave_freq = 0.1  # Wave frequency (Hz)
    modulation = 0.5 + 0.5 * np.sin(2 * np.pi * wave_freq * t)
    
    ocean_sound = noise * modulation
    
    # Smooth the sound
    from scipy import signal
    b, a = signal.butter(3, 0.1, btype='low')
    ocean_sound = signal.filtfilt(b, a, ocean_sound)
    
    # Normalize
    ocean_sound = ocean_sound / np.max(np.abs(ocean_sound))
    
    # Convert to stereo
    stereo_sound = np.column_stack((ocean_sound, ocean_sound))
    stereo_sound = (stereo_sound * 32767).astype(np.int16)
    
    return stereo_sound, sample_rate


def generate_rain_sound(duration_ms, sample_rate=44100):
    """Generate rain sound"""
    duration_s = duration_ms / 1000.0
    num_samples = int(sample_rate * duration_s)
    
    # Multiple layers of filtered noise
    rain = np.zeros(num_samples)
    
    for i in range(3):
        noise = np.random.normal(0, 1, num_samples)
        
        # Different frequency bands for each layer
        from scipy import signal
        b, a = signal.butter(2, 0.2 + i * 0.1, btype='low')
        filtered = signal.filtfilt(b, a, noise)
        
        rain += filtered
    
    # Normalize
    rain = rain / np.max(np.abs(rain))
    
    # Convert to stereo
    stereo_rain = np.column_stack((rain, rain))
    stereo_rain = (stereo_rain * 32767).astype(np.int16)
    
    return stereo_rain, sample_rate


def generate_ambient_pad(duration_ms, sample_rate=44100):
    """Generate soft ambient pad sound"""
    duration_s = duration_ms / 1000.0
    t = np.linspace(0, duration_s, int(sample_rate * duration_s), False)
    
    # Multiple sine waves with slow modulation
    freqs = [110, 165, 220, 330]  # A2, E3, A3, E4
    pad = np.zeros(len(t))
    
    for freq in freqs:
        # Slow amplitude modulation
        mod_freq = 0.05 + np.random.random() * 0.05
        modulation = 0.3 + 0.7 * np.sin(2 * np.pi * mod_freq * t)
        
        wave = np.sin(2 * np.pi * freq * t) * modulation
        pad += wave
    
    # Add subtle noise
    noise = np.random.normal(0, 0.05, len(t))
    pad += noise
    
    # Normalize
    pad = pad / np.max(np.abs(pad))
    
    # Convert to stereo with slight difference for width
    left = pad * 0.9
    right = pad * 1.0
    stereo_pad = np.column_stack((left, right))
    stereo_pad = (stereo_pad * 32767).astype(np.int16)
    
    return stereo_pad, sample_rate


def create_audio_from_array(audio_array, sample_rate):
    audio = AudioSegment(
        audio_array.tobytes(),
        frame_rate=sample_rate,
        sample_width=2,
        channels=2
    )
    return audio


def mix_audios(dialog_audio, background_audio, background_volume_percent):
    background_adjusted = background_audio - (100 - background_volume_percent)
    mixed = dialog_audio.overlay(background_adjusted, loop=True)
    return mixed


def ambient(input_wav, ambient_type='rain', volume=60, output_mp3=None, bitrate='320k'):
    if not os.path.exists(input_wav):
        print(f"Error: No se encontró el archivo '{input_wav}'")
        return None

    if output_mp3:
        output_path = output_mp3
    else:
        base_name = os.path.splitext(input_wav)[0]
        output_path = f"{base_name}.mp3"

    print(f'Cargando audio de diálogo...')
    audio_data, sample_rate = sf.read(input_wav)

    if len(audio_data.shape) == 1:
        audio_data = np.column_stack((audio_data, audio_data))

    audio_data_int16 = (audio_data * 32767).astype(np.int16)

    dialog_audio = AudioSegment(
        audio_data_int16.tobytes(),
        frame_rate=sample_rate,
        sample_width=2,
        channels=audio_data.shape[1]
    )
    duration_ms = len(dialog_audio)

    print(f'Generando sonido ambiental ({ambient_type})...')

    if ambient_type == 'pink':
        bg_audio_array, bg_sample_rate = generate_pink_noise(duration_ms)
    elif ambient_type == 'brown':
        bg_audio_array, bg_sample_rate = generate_brown_noise(duration_ms)
    elif ambient_type == 'ocean':
        bg_audio_array, bg_sample_rate = generate_ocean_waves(duration_ms)
    elif ambient_type == 'rain':
        bg_audio_array, bg_sample_rate = generate_rain_sound(duration_ms)
    elif ambient_type == 'pad':
        bg_audio_array, bg_sample_rate = generate_ambient_pad(duration_ms)

    background_audio = create_audio_from_array(bg_audio_array, bg_sample_rate)

    print(f'Mezclando audios (fondo al {volume}%)...')
    mixed_audio = mix_audios(dialog_audio, background_audio, volume)

    print(f'Exportando a MP3 ({bitrate})...')
    mixed_audio.export(output_path, format='mp3', bitrate=bitrate)
    print(f'Archivo guardado: {output_path}')

    os.remove(input_wav)
    print(f'Archivo temporal eliminado: {input_wav}')

    return output_path


def parse_args():
    parser = argparse.ArgumentParser(description='Add ambient background to audio')
    parser.add_argument('input_wav', help='Path to input WAV file (dialog)')
    parser.add_argument('--output-mp3', help='Output MP3 file path (default: input name + .mp3)')
    parser.add_argument('--type', choices=['pink', 'brown', 'ocean', 'rain', 'pad'], 
                       default='rain', help='Background type (default: rain)')
    parser.add_argument('--volume', type=int, default=60, help='Background volume percentage (default: 60)')
    parser.add_argument('--bitrate', default='320k', help='MP3 bitrate (default: 320k, options: 128k, 192k, 256k, 320k)')
    return parser.parse_args()


def main():
    args = parse_args()
    ambient(args.input_wav, args.type, args.volume, args.output_mp3, args.bitrate)


if __name__ == '__main__':
    main()

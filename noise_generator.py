import numpy as np
from scipy.io.wavfile import write
from scipy import signal
import argparse

def generate_white_noise(length):
    return np.random.randn(length)

def generate_pink_noise(length):
    white = np.random.randn(length)
    b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
    a = [1, -2.494956002, 2.017265875, -0.522189400]
    return signal.lfilter(b, a, white)

def generate_brown_noise(length, sample_rate):
    """
    Generates brown noise and cleans it of inaudible sub-sonic energy
    using a high-pass filter. This is the crucial step to make it
    normalize correctly and be clearly audible.
    """
    white_noise = np.random.randn(length)
    brown_noise = np.cumsum(white_noise)
    detrended_noise = signal.detrend(brown_noise)
    
    # CRUCIAL FIX: Apply a high-pass filter at 20Hz
    nyquist = 0.5 * sample_rate
    cutoff_hz = 20.0
    sos = signal.butter(1, cutoff_hz / nyquist, btype='high', output='sos')
    filtered_noise = signal.sosfilt(sos, detrended_noise)
    
    return filtered_noise

def generate_grey_noise(length, sample_rate):
    """
    Generates grey noise by precisely shaping the spectrum of white noise
    to match an inverse psychoacoustic equal-loudness curve (A-weighting).
    This is achieved using FFT for maximum accuracy, based on the visual
    EQ curve provided.
    """
    white_noise = np.random.randn(length)
    
    # Go to the frequency domain
    fft_noise = np.fft.rfft(white_noise)
    fft_freqs = np.fft.rfftfreq(length, d=1./sample_rate)

    # Define the EQ curve based on the visual reference (fader positions)
    # Frequencies (Hz) and their corresponding gain in dB
    # These points approximate the "smiley face" curve from the screenshot
    freq_points = np.array([    20,   100,   500,  1000,  2000,  4000,  8000, 16000])
    gain_points_db = np.array([ +12,    +4,    -2,    -8,   -10,    -4,    +2,    +8])

    # Interpolate to get a smooth gain curve for all frequencies
    # We use a very small frequency at the start to handle the 0 Hz (DC) component
    interpolated_gains_db = np.interp(fft_freqs, freq_points, gain_points_db, left=gain_points_db[0], right=gain_points_db[-1])
    
    # Convert dB gains to a linear amplitude multiplier
    filter_gains = 10**(interpolated_gains_db / 20)
    
    # Apply the filter in the frequency domain
    filtered_fft = fft_noise * filter_gains
    
    # Go back to the time domain
    grey_noise = np.fft.irfft(filtered_fft, n=length)
    
    return grey_noise

def generate_layered_noise(noise_type, length, sample_rate, num_layers=7):
    base_noise = generate_noise(noise_type, length, sample_rate)
    if num_layers <= 1: return base_noise
    edges = np.logspace(np.log10(20), np.log10(min(20000, sample_rate / 2.1)), num_layers + 1)
    filter_order, nyquist = 4, 0.5 * sample_rate
    noise_layers = []
    for i in range(num_layers):
        low, high = edges[i] / nyquist, edges[i+1] / nyquist
        sos = signal.butter(filter_order, [low, high], btype='band', output='sos')
        filtered_noise = signal.sosfilt(sos, base_noise)
        noise_layers.append(filtered_noise)
    return np.sum(noise_layers, axis=0)

def generate_noise(noise_type, length, sample_rate):
    noise_generators = {
        'white': generate_white_noise, 'pink': generate_pink_noise,
        'brown': lambda l: generate_brown_noise(l, sample_rate),
        'grey': lambda l: generate_grey_noise(l, sample_rate)
    }
    if noise_type not in noise_generators:
        raise ValueError(f"Unknown noise type: {noise_type}. Available types: {list(noise_generators.keys())}")
    return noise_generators[noise_type](length)

def normalize_audio(audio_data):
    audio_data = np.nan_to_num(audio_data)
    initial_rms = np.sqrt(np.mean(audio_data**2))
    if initial_rms == 0: return audio_data
    target_rms = 0.15
    scaled_audio = audio_data * (target_rms / initial_rms)
    peak_level = np.max(np.abs(scaled_audio))
    if peak_level > 1.0:
        return scaled_audio / peak_level
    return scaled_audio

def convert_to_int16(audio_data):
    return np.clip(audio_data * 32767, -32768, 32767).astype(np.int16)

def main():
    parser = argparse.ArgumentParser(description='Generate various types of noise')
    parser.add_argument('--noise-type', choices=['white', 'pink', 'brown', 'grey'], default='white', help='Type of noise')
    parser.add_argument('--layered', action='store_true', help='Generate layered noise')
    parser.add_argument('--duration', type=float, default=0.05, help='Duration in minutes')
    parser.add_argument('--sample-rate', type=int, default=44100, help='Sample rate in Hz')
    parser.add_argument('--output', type=str, default='noise_output.wav', help='Output filename')
    parser.add_argument('--num-layers', type=int, default=7, help='Number of layers for layered noise')
    args = parser.parse_args()
    
    noise_length = int(args.duration * 60 * args.sample_rate)
    print(f"Generating {args.noise_type} noise... (Length: {noise_length:,} samples)")
    
    if args.layered:
        audio_data = generate_layered_noise(args.noise_type, noise_length, args.sample_rate, args.num_layers)
    else:
        audio_data = generate_noise(args.noise_type, noise_length, args.sample_rate)
    
    audio_data = normalize_audio(audio_data)
    audio_data_int16 = convert_to_int16(audio_data)

    write(args.output, args.sample_rate, audio_data_int16)
    print(f"Noise generated successfully! Output file: {args.output}")

if __name__ == "__main__":
    main()
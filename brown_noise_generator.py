import numpy as np
from scipy.io.wavfile import write
from scipy import signal

# Parameters for the brown noise generation
sample_rate = 44100  # Sample rate in Hz
duration_hours = 1  # Duration of the audio in hours
noise_length = duration_hours * sample_rate * 3600  # Total number of samples

# Generate white noise
white_noise = np.random.randn(noise_length)

# Define frequency bands and corresponding low-pass filter parameters
freq_bands = [5, 10, 20, 40, 80, 160, 320]  # Frequency bands in Hz
filter_order = 4
low_pass_filters = []

for freq in freq_bands:
    # Nyquist frequency calculation fixed
    nyquist = sample_rate / 2
    b, a = signal.butter(filter_order, freq / nyquist, btype='low')
    low_pass_filters.append((b, a))

# Generate multiple layers of brown noise with different frequencies
brown_noise_layers = []
for b, a in low_pass_filters:
    # Remove the unnecessary convolution - just apply the Butterworth filter
    filtered_noise = signal.lfilter(b, a, white_noise)
    brown_noise_layers.append(filtered_noise)

# Mix all layers together (fix the stacking issue)
brown_noise_mixed = np.sum(brown_noise_layers, axis=0)

# Normalize the noise to be within the range [-1, 1]
max_val = np.max(np.abs(brown_noise_mixed))
if max_val > 0:  # Avoid division by zero
    brown_noise_mixed = brown_noise_mixed / max_val

# Convert to int16 as required by .wav file format
# Use proper scaling for int16 range
audio_data = np.clip(brown_noise_mixed * 32767, -32768, 32767).astype(np.int16)

# Write the audio data to a .wav file
write('brown_noise.wav', sample_rate, audio_data)

print(f"Brown noise generated successfully!")
print(f"Duration: {duration_hours} hour(s)")
print(f"Sample rate: {sample_rate} Hz")
print(f"File size: approximately {len(audio_data) * 2 / (1024*1024):.1f} MB")
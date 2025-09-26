Noise Generator 🎧

This Python noise_generator_eq generates different types of noise (white, pink, brown, grey, etc.) by applying spectral shaping to white noise based on customizable EQ profiles.
The output is saved as a .wav file.

⸻

Features
	•	Multiple built-in noise profiles:
	•	white: Flat energy across all frequencies
	•	grey_screenshot: “Bathtub”-shaped curve with boosted lows and highs
	•	brown_screenshot: Very bass-heavy, based on EQ curve from screenshot
	•	pink_technical: Drops by –3 dB per octave (more natural than white noise)
	•	brown_technical: Drops by –6 dB per octave (deep, waterfall-like sound)
	•	Easy to extend: add new profiles to the EQ_PRESETS dictionary.
	•	Normalization ensures safe output levels.
	•	Exports to .wav for easy playback.

⸻

Installation

This project uses uv to run.
Make sure you have it installed, then you can run the noise_generator_eq directly:

uv run noise_generator_eq.py --help

Dependencies (uv will handle these automatically if you specify them in your environment):
	•	numpy
	•	scipy

⸻

Usage

Run the noise_generator_eq with:

uv run noise_generator_eq.py [OPTIONS]

Options

Option	Default	Denoise_generator_eqion
--noise-type	white	Type of noise to generate. Available: white, grey_screenshot, brown_screenshot, pink_technical, brown_technical
--duration	1.0	Duration in minutes
--sample-rate	44100	Sample rate in Hz
--output	noise_output.wav	Output filename


⸻

Examples

Generate 10 minutes of pink noise at 48 kHz:

uv run noise_generator_eq.py --noise-type pink_technical --duration 10 --sample-rate 48000 --output pink.wav

Generate 5 minutes of bass-heavy brown noise:

uv run noise_generator_eq.py --noise-type brown_screenshot --duration 5 --output brown.wav


⸻

Adding Custom Noise Profiles

To create your own noise type:
	1.	Open noise_generator_eq.py
	2.	Add a new entry to the EQ_PRESETS dictionary, e.g.:

"my_noise": {
    "denoise_generator_eqion": "Custom profile with boosted mids.",
    "freqs":    [20, 500, 2000, 8000, 20000],
    "gains_db": [ 0,  +5,   +3,   -2,    0]
}

	3.	Run it with:

uv run noise_generator_eq.py --noise-type my_noise


⸻

Output
	•	Audio is normalized to safe levels (target RMS ≈ 0.15).
	•	The .wav file is saved in 16-bit PCM format, compatible with most players.


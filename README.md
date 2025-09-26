# **Noise Generator 🎧**

This Python script generates different types of noise (white, pink, brown, grey, etc.) by applying spectral shaping to white noise based on customizable EQ profiles.

The output is saved as a .wav file.

* * *

## **Features**

- Multiple built-in noise profiles:
    - **white**: Flat energy across all frequencies
    - **grey\_screenshot**: “Bathtub”-shaped curve with boosted lows and highs
    - **brown\_screenshot**: Very bass-heavy, based on EQ curve from screenshot
    - **pink\_technical**: Drops by –3 dB per octave (more natural than white noise)
    - **brown\_technical**: Drops by –6 dB per octave (deep, waterfall-like sound)

- Easy to extend: add new profiles to the EQ\_PRESETS dictionary.
- Normalization ensures safe output levels.
- Exports to .wav for easy playback.

* * *

## **Installation**

This project uses [uv](https://github.com/astral-sh/uv) to run.

Make sure you have it installed, then you can run the script directly:

```
uv run script.py --help
```

Dependencies (uv will handle these automatically if you specify them in your environment):

- numpy
- scipy

* * *

## **Usage**

Run the script with:

```bash
uv run script.py [OPTIONS]
```

### **Options**

| **Option** | **Default** | **Description** |
| --- | --- | --- |
| \--noise-type | white | Type of noise to generate. Available: white, grey\_screenshot, brown\_screenshot, pink\_technical, brown\_technical |
| \--duration | 1.0 | Duration in **minutes** |
| \--sample-rate | 44100 | Sample rate in Hz |
| \--output | noise\_output.wav | Output filename |

* * *

### **Examples**

<br>

Generate **10 minutes of pink noise** at 48 kHz:

```
uv run script.py --noise-type pink_technical --duration 10 --sample-rate 48000 --output pink.wav
```

Generate **5 minutes of bass-heavy brown noise**:

```
uv run script.py --noise-type brown_screenshot --duration 5 --output brown.wav
```

* * *

## **Adding Custom Noise Profiles**

To create your own noise type:

1. Open script.py
2. Add a new entry to the EQ\_PRESETS dictionary, e.g.:

```
"my_noise": {
    "description": "Custom profile with boosted mids.",
    "freqs":    [20, 500, 2000, 8000, 20000],
    "gains_db": [ 0,  +5,   +3,   -2,    0]
}
```

3. Run it with:

```
uv run script.py --noise-type my_noise
```

* * *

## **Output**

- Audio is normalized to safe levels (target RMS ≈ 0.15).
- The .wav file is saved in 16-bit PCM format, compatible with most players.

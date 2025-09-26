import numpy as np
from scipy.io.wavfile import write
from scipy import signal
import argparse

# =============================================================================
# 1. ZENTRALE DATENSTRUKTUR FÜR EQ-PROFILE (DEINE IDEE!)
# =============================================================================
# Hier definieren wir alle Rauscharten über ihre Frequenzkurven.
# Du kannst hier ganz einfach neue Rauscharten hinzufügen!
# 'freqs' sind die Frequenzpunkte in Hz.
# 'gains_db' ist die Anhebung/Absenkung in Dezibel (dB) an diesen Punkten.

EQ_PRESETS = {
    # Klassisches weißes Rauschen: Eine komplett flache Kurve.
    "white": {
        "description": "Alle Frequenzen haben die gleiche Energie.",
        "freqs":    [   20, 20000],
        "gains_db": [    0,     0]
    },
    # Grey Noise, wie von deinem ersten Screenshot abgelesen.
    # Dies ist eine "Badewannen"-Kurve, die Bässe und Höhen betont.
    "grey_screenshot": {
        "description": "Perzeptuelles Rauschen basierend auf der EQ-Kurve im Screenshot.",
        "freqs":    [   30,    60,   120,   250,   500,  1000,  2000,  4000,  8000, 16000],
        "gains_db": [ +5.0,  +2.0,  +0.0,  -2.0,  -4.0,  -6.0,  -4.5,  -1.5,  +1.0,  +4.0]
    },
    # Brown Noise, wie von deinem letzten Screenshot abgelesen.
    # Eine stark abfallende Kurve, die Bässe massiv betont.
    "brown_screenshot": {
        "description": "Sehr basslastiges Rauschen basierend auf der EQ-Kurve im Screenshot.",
        "freqs":    [   30,    60,   120,   250,   500,  1000,  2000,  4000,  8000, 16000],
        "gains_db": [ +6.0,  +4.0,  +2.0,  -0.5,  -3.0,  -5.5,  -8.0, -10.0, -12.0, -14.0]
    },
    # Technisch korrektes Rosa Rauschen (-3 dB pro Oktave)
    "pink_technical": {
        "description": "Energie fällt mit 3 dB pro Oktave ab. Klingt natürlicher als weißes Rauschen.",
        "freqs":    [   20,   100,   400,  1600,  6400, 20000],
        "gains_db": [    0,    -7,   -13,   -19,   -25,   -29] # 10*log10(1/f)
    },
    # Technisch korrektes Braunes Rauschen (-6 dB pro Oktave)
    "brown_technical": {
        "description": "Energie fällt mit 6 dB pro Oktave ab. Sehr dumpf, wie ein Wasserfall.",
        "freqs":    [   20,   100,   400,  1600,  6400, 20000],
        "gains_db": [    0,   -14,   -26,   -38,   -50,   -58] # 20*log10(1/f)
    }
}


# =============================================================================
# 2. DIE NEUE, UNIVERSELLE RAUSCH-GENERATOR-FUNKTION
# =============================================================================
# Diese Funktion ersetzt alle alten Generatoren (white, pink, brown, grey).
# Sie nimmt ein Profil aus unserem Dictionary und erzeugt das passende Rauschen.

def generate_noise_from_profile(length, sample_rate, profile):
    """
    Generiert Rauschen durch spektrale Formung von weißem Rauschen
    basierend auf einem gegebenen EQ-Profil.
    """
    # Schritt 1: Erzeuge das Rohmaterial - weißes Rauschen
    white_noise = np.random.randn(length)
    
    # Schritt 2: Wechsle in den Frequenzraum mittels FFT
    fft_noise = np.fft.rfft(white_noise)
    fft_freqs = np.fft.rfftfreq(length, d=1./sample_rate)

    # Schritt 3: Erzeuge die detaillierte Filterkurve aus dem Profil
    # Wir interpolieren zwischen den Punkten, um eine glatte Kurve zu erhalten.
    freq_points = profile['freqs']
    gain_points_db = profile['gains_db']
    
    # np.interp ist der Schlüssel: Es berechnet die Gain-Werte für ALLE Frequenzen der FFT.
    interpolated_gains_db = np.interp(fft_freqs, freq_points, gain_points_db)
    
    # Schritt 4: Wandle die dB-Werte in einen linearen Multiplikator um
    # Eine Anhebung um 6 dB bedeutet z.B. eine Verdopplung der Amplitude.
    filter_gains = 10**(interpolated_gains_db / 20)
    
    # Wichtiger Fix: Der 0-Hz-Anteil (DC-Offset) sollte immer 0 sein.
    filter_gains[0] = 0
    
    # Schritt 5: Wende den Filter an, indem du die Spektren multiplizierst
    filtered_fft = fft_noise * filter_gains
    
    # Schritt 6: Wechsle zurück in den Zeitbereich (unsere Audio-Welle)
    custom_noise = np.fft.irfft(filtered_fft, n=length)
    
    return custom_noise


# =============================================================================
# 3. HELFERFUNKTIONEN (Normalisierung, Konvertierung) - unverändert
# =============================================================================

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

# =============================================================================
# 4. HAUPTPROGRAMM - MODIFIZIERT, UM DIE NEUE STRUKTUR ZU NUTZEN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Generiert verschiedene Rauscharten basierend auf EQ-Profilen.',
        formatter_class=argparse.RawTextHelpFormatter # Für schönere Hilfe-Ausgabe
    )
    
    # Erzeuge die Hilfe-Texte dynamisch aus unserem Preset-Dictionary
    profile_help = "Art des zu generierenden Rauschens. Verfügbare Profile:\n"
    for name, profile in EQ_PRESETS.items():
        profile_help += f"  - {name}: {profile['description']}\n"
        
    parser.add_argument(
        '--noise-type', 
        choices=EQ_PRESETS.keys(), 
        default='white', 
        help=profile_help
    )
    parser.add_argument('--duration', type=float, default=1.0, help='Dauer in Minuten')
    parser.add_argument('--sample-rate', type=int, default=44100, help='Sample rate in Hz')
    parser.add_argument('--output', type=str, default='noise_output.wav', help='Name der Output-Datei')
    args = parser.parse_args()
    
    noise_length = int(args.duration * 60 * args.sample_rate)
    
    # Wähle das gewünschte Profil aus dem Dictionary
    selected_profile = EQ_PRESETS[args.noise_type]
    
    print(f"Generiere Rauschen mit Profil '{args.noise_type}'...")
    print(f"Beschreibung: {selected_profile['description']}")
    print(f"Länge: {noise_length:,} Samples")
    
    # Rufe unsere neue, universelle Funktion auf
    audio_data = generate_noise_from_profile(noise_length, args.sample_rate, selected_profile)
    
    # Normalisieren und speichern (wie zuvor)
    audio_data = normalize_audio(audio_data)
    audio_data_int16 = convert_to_int16(audio_data)

    write(args.output, args.sample_rate, audio_data_int16)
    print(f"Rauschen erfolgreich generiert! Output-Datei: {args.output}")

if __name__ == "__main__":
    main()
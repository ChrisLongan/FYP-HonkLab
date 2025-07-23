import numpy as np
from rtlsdr import RtlSdr
import time

# === CONFIGURATION ===
SAMPLE_RATE = 250_000  # Hz
FREQ = 433.92e6        # 433.92 MHz
GAIN = 'auto'
THRESHOLD = 0.02       # Amplitude change threshold 
DURATION = 3           # Capture duration in seconds
TXT_FILE = "signal_timings.txt"

def iq_to_amplitude(iq):
    return np.abs(iq)

def detect_edges(amplitude, threshold=THRESHOLD):
    digital = amplitude > threshold
    changes = np.diff(digital.astype(int))
    edge_indices = np.where(changes != 0)[0]
    return edge_indices

def main():
    print("Starting RTL-SDR capture...")
    sdr = RtlSdr()
    sdr.sample_rate = SAMPLE_RATE
    sdr.center_freq = FREQ
    sdr.gain = GAIN

    num_samples = int(SAMPLE_RATE * DURATION)
    iq = sdr.read_samples(num_samples)
    sdr.close()
    print(f"✅ Captured {len(iq)} samples")

    amplitude = iq_to_amplitude(iq)
    edges = detect_edges(amplitude)
    print(f"🔍 Found {len(edges)} signal edges")

    # Convert to pulse durations (microseconds)
    pulses = np.diff(edges) * (1_000_000 / SAMPLE_RATE)

    # Save to txt
    with open(TXT_FILE, "w") as f:
        for pulse in pulses:
            f.write(f"{int(pulse)}\n")

    print(f"📝 Saved {len(pulses)} pulses to {TXT_FILE}")

if __name__ == "__main__":
    main()

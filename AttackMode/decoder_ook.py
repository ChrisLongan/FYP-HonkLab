# OOK Decoder for 433 MHz Key Fob Signals
# Compatible with pulse timing output from RTL-SDR capture

from decoder_stor import store_decoded_payload

SHORT_MIN = 200     # µs, adjust based on actual signals
SHORT_MAX = 800
LONG_MIN = 800
LONG_MAX = 1800
SYNC_THRESHOLD = 3000  # µs (marks gap between frames)

INPUT_FILE = "signal_timings.txt"

def classify_bit(high, low):
    # Basic classifier for fixed-code OOK (like PT2262 or EV1527)
    if SHORT_MIN <= high <= SHORT_MAX and SHORT_MIN <= low <= SHORT_MAX:
        return "0"
    elif SHORT_MIN <= high <= SHORT_MAX and LONG_MIN <= low <= LONG_MAX:
        return "1"
    else:
        return None

def decode_pulses(pulses):
    bits = ""
    frames = []

    i = 0
    while i + 1 < len(pulses):
        high = pulses[i]
        low = pulses[i + 1]

        if high > SYNC_THRESHOLD:
            if len(bits) >= 8:
                frames.append(bits)
            bits = ""
            i += 1
            continue

        bit = classify_bit(high, low)
        if bit is not None:
            bits += bit
            i += 2
        else:
            i += 1  # Skip bad pulse

    if len(bits) >= 8:
        frames.append(bits)

    return frames

def main():
    with open(INPUT_FILE, "r") as f:
        pulses = [int(line.strip()) for line in f if line.strip().isdigit()]

    print(f"Loaded {len(pulses)} pulses")

    decoded = decode_pulses(pulses)
    print(f"Found {len(decoded)} valid frame(s):\n")

    for i, frame in enumerate(decoded):
        hex_val = hex(int(frame, 2))[2:].upper()
        print(f"[Frame {i+1}] Binary: {frame} | Hex: {hex_val}")
        store_decoded_payload(hex_val, decoder_type="ook")

if __name__ == "__main__":
    main()

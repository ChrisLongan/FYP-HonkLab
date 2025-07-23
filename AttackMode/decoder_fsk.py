import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from decoder_stor import store_decoded_payload

def fsk_decode(signal, sample_rate, mark_freq, space_freq, baudrate):
    bit_period = int(sample_rate / baudrate)
    num_bits = len(signal) // bit_period
    bits = ""

    for i in range(num_bits):
        chunk = signal[i * bit_period : (i + 1) * bit_period]

        # Simple FFT to determine dominant frequency
        fft_vals = np.abs(np.fft.fft(chunk))
        freqs = np.fft.fftfreq(len(chunk), d=1/sample_rate)
        peak_freq = freqs[np.argmax(fft_vals[:len(fft_vals)//2])]

        if abs(peak_freq - mark_freq) < abs(peak_freq - space_freq):
            bits += "1"
        else:
            bits += "0"

    return bits

def main():
    input_path = "fsk_recorded_signal.npy"
    signal = np.load(input_path)
    sample_rate = 250000  # in Hz
    mark_freq = 12000     # Hz
    space_freq = 10000    # Hz
    baudrate = 1000       # bits/sec

    decoded_bits = fsk_decode(signal, sample_rate, mark_freq, space_freq, baudrate)
    hex_val = hex(int(decoded_bits, 2))[2:].zfill(16)
    print(f"Decoded FSK Bits: {decoded_bits}")
    print(f"Hex: {hex_val.upper()}")

    store_decoded_payload(hex_val, decoder_type="fsk")

if __name__ == "__main__":
    main()

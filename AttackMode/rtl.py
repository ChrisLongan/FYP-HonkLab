from rtlsdr import RtlSdr
import matplotlib.pyplot as plt
import numpy as np

# --- SDR Configuration ---
sdr = RtlSdr()
sdr.sample_rate = 2.4e6      # 2.4 MS/s
sdr.center_freq = 433.92e6   # 433.92 MHz (car key fob freq)
sdr.gain = 'auto'

# --- Signal Capture ---
print("[INFO] Reading samples...")
samples = sdr.read_samples(256*1024)
sdr.close()

# --- FFT Computation ---
print("[INFO] Processing FFT...")
power = 20*np.log10(np.abs(np.fft.fftshift(np.fft.fft(samples))))
freqs = np.fft.fftshift(np.fft.fftfreq(len(samples), 1/sdr.sample_rate))

# --- Plotting ---
plt.figure(figsize=(10, 5))
plt.plot(freqs/1e6 + sdr.center_freq/1e6, power, color='blue')
plt.title(f"Spectrum | Fc={sdr.center_freq/1e6:.2f} MHz, Fs={sdr.sample_rate/1e6:.2f} MHz")
plt.xlabel("Frequency (MHz)")
plt.ylabel("Power (dB)")
plt.grid(True)
plt.tight_layout()
plt.show()

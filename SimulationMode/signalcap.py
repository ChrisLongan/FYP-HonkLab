from rtlsdr import RtlSdr
import matplotlib.pyplot as plt
import numpy as np

def signalview():
    try:
        print("[INFO] Initializing RTL-SDR...")
        sdr = RtlSdr()

        # === Basic Checks ===
        if sdr is None:
            print("[ERROR] RTL-SDR device not found.")
            return

        # === Safe SDR Configuration ===
        sdr.sample_rate = 2.4e6      # 2.4 MS/s
        sdr.center_freq = 433.92e6   # Car key fob freq
        sdr.gain = 'auto'

        print(f"[✓] SDR Configured: Fc={sdr.center_freq} Hz, Fs={sdr.sample_rate} Hz")

        # === Signal Capture ===
        print("[INFO] Reading samples...")
        samples = sdr.read_samples(256 * 1024)
        sdr.close()

        if len(samples) == 0:
            print("[ERROR] No samples captured!")
            return

        # === FFT Computation ===
        print("[INFO] Processing FFT...")
        power = 20 * np.log10(np.abs(np.fft.fftshift(np.fft.fft(samples))))
        freqs = np.fft.fftshift(np.fft.fftfreq(len(samples), 1 / sdr.sample_rate))

        # === Plotting ===
        print("[INFO] Plotting FFT...")
        plt.figure(figsize=(10, 5))
        plt.plot(freqs / 1e6 + sdr.center_freq / 1e6, power, color='blue')
        plt.title(f"Spectrum | Fc={sdr.center_freq/1e6:.2f} MHz, Fs={sdr.sample_rate/1e6:.2f} MHz")
        plt.xlabel("Frequency (MHz)")
        plt.ylabel("Power (dB)")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    except ZeroDivisionError:
        print("[ERROR] Sample rate or frequency is zero — check RTL-SDR connection and retry.")
    except Exception as e:
        print(f"[ERROR] Unexpected failure: {e}")
    finally:
        try:
            sdr.close()
        except:
            pass

if __name__ == "__main__":
    signalview()

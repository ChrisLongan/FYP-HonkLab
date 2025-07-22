from rtlsdr import RtlSdr
import matplotlib.pyplot as plt
import numpy as np

sdr = RtlSdr()

sdr.sample_rate = 2.4e6       # Hz
sdr.center_freq = 433.92e6    # Hz
sdr.gain = 'auto'

samples = sdr.read_samples(256*1024)
sdr.close()

# Plot signal power spectrum
plt.psd(samples, NFFT=1024, Fs=sdr.sample_rate / 1e6, Fc=sdr.center_freq / 1e6)
plt.xlabel('Frequency (MHz)')
plt.ylabel('Relative power (dB)')
plt.title('RTL-SDR Spectrum at 433.92 MHz')
plt.show()

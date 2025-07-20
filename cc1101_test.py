import spidev
import time

# Open SPI bus 1, device 0
spi = spidev.SpiDev()
spi.open(1, 0)  # SPI1, CS0 (usually mapped via dtoverlay cs0_pin)
spi.max_speed_hz = 500000

# CC1101 command strobe: SRES (reset)
CC1101_SRES = 0x30

# Send SRES and read back 1 byte
resp = spi.xfer2([CC1101_SRES, 0x00])
print("Response from CC1101:", resp)

spi.close()

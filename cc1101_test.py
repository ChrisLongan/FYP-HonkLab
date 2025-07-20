import spidev
import RPi.GPIO as GPIO
import time


CS_GPIO = 24 
VERSION_REG = 0x0D | 0x80  # Read single-byte from register 0x0D


# Open SPI bus 1, device 0
spi = spidev.SpiDev()
spi.open(1, 0)  # SPI1, CS0 (usually mapped via dtoverlay cs0_pin)
spi.max_speed_hz = 500000

GPIO.setmode(GPIO.BCM)
GPIO.setup(CS_GPIO, GPIO.OUT)
GPIO.output(CS_GPIO, GPIO.LOW)

# Send SRES strobe (0x30) + dummy
sres_resp = spi.xfer2([0x30, 0x00])
print("SRES Response (Reset Strobe):", sres_resp)

# Read version register
version_resp = spi.xfer2([VERSION_REG, 0x00])
print("CC1101 Version Register (0x0D):", hex(version_resp[1]))

# Cleanup
GPIO.output(CS_GPIO, GPIO.HIGH)
GPIO.cleanup()
spi.close()

# CC1101 command strobe: SRES (reset)
CC1101_SRES = 0x30

# Send SRES and read back 1 byte
resp = spi.xfer2([CC1101_SRES, 0x00])
print("Response from CC1101:", resp)

spi.close()

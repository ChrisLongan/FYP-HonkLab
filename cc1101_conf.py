import bitbangspi
import RPi.GPIO as GPIO
import time

# GPIO Pins (BCM Mode)
SCK  = 21
MOSI = 20
MISO = 19
CSN  = 18
GDO0 = 26
GDO2 = 16

# Setup GPIO for GDO monitoring
GPIO.setmode(GPIO.BCM)
GPIO.setup(GDO0, GPIO.IN)
GPIO.setup(GDO2, GPIO.IN)

# Initialize software SPI
spi = bitbangspi.SPI(
    sclk=SCK,
    mosi=MOSI,
    miso=MISO,
    cs=CSN
)
spi.set_speed_hz(500000)

print("🔁 Sending SRES (Reset Strobe)...")
response = spi.transfer([0x30, 0x00])
print("SRES Response:", response)

# Read version register (0x0D)
version_reg = 0x0D | 0x80  # 0x8D for read
version_resp = spi.transfer([version_reg, 0x00])
print("📟 CC1101 Version Register:", hex(version_resp[1]))

# Read GDO lines
gdo0_val = GPIO.input(GDO0)
gdo2_val = GPIO.input(GDO2)
print(f"📡 GDO0 (GPIO {GDO0}) State: {'HIGH' if gdo0_val else 'LOW'}")
print(f"📡 GDO2 (GPIO {GDO2}) State: {'HIGH' if gdo2_val else 'LOW'}")

# Cleanup
spi.close()
GPIO.cleanup()

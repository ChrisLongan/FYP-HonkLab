# import spidev
# import time

# # Open SPI bus 1, device 0
# spi = spidev.SpiDev()
# spi.open(1, 0)  # SPI1, CS0 (usually mapped via dtoverlay cs0_pin)
# spi.max_speed_hz = 500000

# # CC1101 command strobe: SRES (reset)
# CC1101_SRES = 0x30

# # Send SRES and read back 1 byte
# resp = spi.xfer2([CC1101_SRES, 0x00])
# print("Response from CC1101:", resp)

# spi.close()

from cc1101_softspi import SoftwareSPI
import time

spi = SoftwareSPI()

try:
    print("[*] Sending RESET strobe (0x30)")
    response = spi.transfer([0x30])
    print("[+] Response:", response)

    print("[*] Reading version register (0x0D)")
    version = spi.transfer([0x8D, 0x00])  # 0x8D = Read single | 0x0D
    print("[+] Version Register Response:", version)

    print("[*] GDO0 =", spi.read_gdo0())
    print("[*] GDO2 =", spi.read_gdo2())

finally:
    spi.cleanup()

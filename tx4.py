# tx_debug_loop.py
from cc1101_conf import SoftwareSPI
import time
import RPi.GPIO as GPIO

spi = SoftwareSPI()

def setup_cc1101():
    print("[*] Resetting CC1101...")
    spi.transfer([0x30])  # SRES
    time.sleep(0.1)

    print("[*] Reading VERSION register...")
    version = spi.transfer([0x8D, 0x00])  # 0x8D = READ | 0x0D
    print("[+] VERSION register response:", version)
    
    if version[1] in [0x14, 0x1E, 0x0F, 0x30]:
        print("[✓] CC1101 responded — SPI communication OK")
    else:
        print("[✗] No valid CC1101 response. Check wiring.")
        return

    print("[*] Forcing CC1101 to IDLE state...")
    spi.transfer([0x36])  # SIDLE
    time.sleep(0.05)

    print("[*] Writing config for 433.92 MHz, 2-FSK...")
    config = {
        0x02: 0x06,  # FREQ2
        0x03: 0x21,  # FREQ1
        0x04: 0x65,  # FREQ0 = 433.92 MHz
        0x0B: 0x06,  # CHANNR
        0x0D: 0x34,  # FSCTRL1
        0x0E: 0x0C,  # FSCTRL0
        0x10: 0x45,  # MDMCFG4
        0x11: 0x43,  # MDMCFG3
        0x12: 0x03,  # MDMCFG2 - 2-FSK, no Manchester
        0x13: 0x22,  # DEVIATN
        0x14: 0x07,  # MCSM2
        0x15: 0x0C,  # MCSM1 - TX after strobe
        0x17: 0x3E,  # PKTLEN = 62 bytes
        0x18: 0x04,  # PKTCTRL1
        0x19: 0x05,  # PKTCTRL0
    }

    for reg, val in config.items():
        spi.write_register(reg, val)
        time.sleep(0.003)

    print("[*] Re-entering IDLE to finalize config...")
    spi.transfer([0x36])  # SIDLE
    time.sleep(0.05)

    print("[+] CC1101 configured.")

def send_debug_burst(i):
    print(f"\n[*] Sending burst {i+1}/10...")

    # Force flush TX FIFO before writing new payload
    spi.transfer([0x3B])  # SFTX
    time.sleep(0.01)

    # 62-byte alternating pattern
    payload = []
    for _ in range(31):
        payload.extend([0xA2, 0xF1, 0xD0])

    spi.write_burst(0x3F, payload)
    time.sleep(0.005)

    spi.transfer([0x35])  # STX
    print("[>] STX sent - transmitting...")

    # Poll GDO0 to confirm transmission activity
    for j in range(10):
        gdo0 = spi.read_gdo0()
        print(f"GDO0[{j}] =", gdo0)
        time.sleep(0.05)

try:
    setup_cc1101()
    print("[*] Starting debug TX loop...")

    for i in range(10):
        send_debug_burst(i)
        time.sleep(0.5)

    print("[✓] Debug TX loop finished.")

except KeyboardInterrupt:
    print("\n[!] Interrupted by user.")

finally:
    spi.cleanup()
    GPIO.cleanup()

# tx_loop_easy.py
from cc1101_conf import SoftwareSPI
import time

spi = SoftwareSPI()

def setup_cc1101():
    print("[*] Resetting CC1101...")
    spi.transfer([0x30])  # SRES
    time.sleep(0.1)

    print("[*] Writing basic config...")
    config = {
        0x02: 0x06,   # FREQ2
        0x03: 0x21,   # FREQ1
        0x04: 0x65,   # FREQ0  => 433.92 MHz
        0x0B: 0x06,   # CHANNR
        0x0D: 0x34,   # FSCTRL1
        0x0E: 0x0C,   # FSCTRL0
        0x10: 0x45,   # MDMCFG4
        0x11: 0x43,   # MDMCFG3
        0x12: 0x0B,   # MDMCFG2
        0x13: 0x22,   # DEVIATN
        0x14: 0xF8,   # MCSM2
        0x17: 0x30,   # PKTLEN
        0x18: 0x04,   # PKTCTRL1
        0x19: 0x05,   # PKTCTRL0
    }

    for reg, val in config.items():
        spi.write_register(reg, val)
        time.sleep(0.005)

    print("[+] CC1101 configured.")

def send_burst():
    # Create a very obvious pattern like 0xAA, 0x55, 0xAA, 0x55
    packet = [0x04, 0xAA, 0x55, 0xAA, 0x55]
    spi.write_burst(0x3F, packet)
    spi.transfer([0x35])  # STX
    print("[>] Packet sent")
    time.sleep(0.2)

try:
    setup_cc1101()
    print("[*] Starting continuous burst every 0.5s...")
    while True:
        send_burst()
        time.sleep(0.5)

except KeyboardInterrupt:
    print("[!] Stopped by user")

finally:
    spi.cleanup()

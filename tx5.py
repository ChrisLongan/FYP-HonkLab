# tx_carrier_test.py
from cc1101_conf import SoftwareSPI
import time
import RPi.GPIO as GPIO

spi = SoftwareSPI()

def setup_for_carrier():
    print("[*] Resetting CC1101...")
    spi.transfer([0x30])  # SRES
    time.sleep(0.1)

    print("[*] Setting up carrier frequency at 433.92 MHz...")
    config = {
        0x02: 0x06,  # FREQ2
        0x03: 0x21,  # FREQ1
        0x04: 0x65,  # FREQ0 => 433.92 MHz
        0x0D: 0x34,  # FSCTRL1
        0x0E: 0x0C,  # FSCTRL0
        0x10: 0x45,  # MDMCFG4
        0x11: 0x43,  # MDMCFG3
        0x12: 0x30,  # MDMCFG2 = ASK/OOK, no sync, no preamble
        0x13: 0x00,  # DEVIATN = 0
        0x15: 0x10,  # MCSM1 = Stay in TX
        0x18: 0x00,  # PKTCTRL1
        0x19: 0x00,  # PKTCTRL0 = no whitening, fixed length
    }

    for reg, val in config.items():
        spi.write_register(reg, val)
        time.sleep(0.003)

    print("[*] Flushing TX FIFO...")
    spi.transfer([0x3B])  # SFTX
    time.sleep(0.05)

def transmit_carrier():
    print("[*] Sending unmodulated carrier...")
    spi.transfer([0x35])  # STX (start transmission)
    print("[+] Carrier should now be visible on SDR.")
    print(">>> Press Ctrl+C to stop.")

try:
    setup_for_carrier()
    transmit_carrier()

    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\n[!] Stopping carrier...")

finally:
    spi.transfer([0x36])  # SIDLE
    spi.cleanup()
    GPIO.cleanup()

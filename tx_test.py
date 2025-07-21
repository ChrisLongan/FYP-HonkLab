# tx_test.py
from cc1101_conf import SoftwareSPI
import time

spi = SoftwareSPI()

def cc1101_configure(spi):
    print("[*] Resetting CC1101...")
    spi.transfer([0x30])  # SRES strobe
    time.sleep(0.1)

    print("[*] Writing configuration registers...")
    # Minimal config: frequency 433.92 MHz, GFSK, 2-FSK, 1.2kbps, etc.
    config = {
        0x02: 0x06,   # Frequency Control Word, High Byte
        0x03: 0x21,   # Frequency Control Word, Middle Byte
        0x04: 0x65,   # Frequency Control Word, Low Byte => 433.92 MHz

        0x0B: 0x06,   # Channel BW = 58KHz
        0x0D: 0x34,   # Main Radio Control State Machine
        0x0E: 0x0C,   # Frequency Synthesizer Control
        0x10: 0x45,   # Modem Configuration
        0x11: 0x43,   # Modem Configuration
        0x12: 0x0B,   # Modem Deviation
        0x13: 0x22,   # TX power
        0x14: 0xF8,   # Channel spacing
        0x17: 0x30,   # Packet length
        0x18: 0x04,   # Packet automation
        0x19: 0x05,   # Address check
        0x1E: 0x0C,   # Frequency synthesizer control
    }

    for reg, val in config.items():
        spi.write_register(reg, val)
        time.sleep(0.005)

    print("[*] Configuration complete.")

def cc1101_transmit(spi, packet):
    print("[*] Loading TX FIFO...")
    spi.write_burst(0x3F, packet)  # TX FIFO burst write
    time.sleep(0.1)

    print("[*] Sending STX (Transmit strobe)...")
    spi.transfer([0x35])  # STX: Enable TX mode

    time.sleep(0.2)
    print("[+] Transmission complete.")

try:
    cc1101_configure(spi)

    # Your raw RF packet (example: 0xDE, 0xAD, 0xBE, 0xEF)
    rf_packet = [0x04, 0xDE, 0xAD, 0xBE, 0xEF]  # 0x04 = payload length
    cc1101_transmit(spi, rf_packet)

finally:
    spi.cleanup()
    print("[*] GPIO cleaned up.")

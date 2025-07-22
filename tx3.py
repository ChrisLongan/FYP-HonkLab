# tx_loop_debug.py
from cc1101_conf import SoftwareSPI
import time
import RPi.GPIO as GPIO

spi = SoftwareSPI()

def setup_cc1101():
    print("[*] Resetting CC1101...")
    spi.transfer([0x30])  # SRES
    time.sleep(0.1)

    print("[*] Reading VERSION register...")
    version = spi.transfer([0x8D, 0x00])
    print("[+] VERSION register response:", version)

    if version[1] not in [0x14, 0x1E, 0x0F, 0x30]:
        print("[!] Invalid CC1101 version. Check connections.")
        return False

    print("[*] Writing config registers...")
    config = {
        0x00: 0x06,  # IOCFG2
        0x01: 0x06,  # IOCFG1
        0x02: 0x07,  # IOCFG0 = assert when SYNC TX'd
        0x0B: 0x06,  # CHANNR
        0x0D: 0x34,  # FSCTRL1
        0x0E: 0x0C,  # FSCTRL0
        0x10: 0xF5,  # MDMCFG4 – lower data rate
        0x11: 0x43,  # MDMCFG3
        0x12: 0x0B,  # MDMCFG2
        0x13: 0x22,  # DEVIATN
        0x14: 0x07,  # MCSM2
        0x15: 0x30,  # MCSM1
        0x16: 0x18,  # MCSM0
        0x17: 0x3D,  # FOCCFG
        0x18: 0x04,  # PKTCTRL1
        0x19: 0x05,  # PKTCTRL0
        0x1E: 0xC7,  # WORCTRL
        0x06: 0x21,  # FREQ2
        0x07: 0x65,  # FREQ1
        0x08: 0x6A,  # FREQ0 = 433.92 MHz
        0x17: 0x30   # PKTLEN
    }

    for reg, val in config.items():
        spi.write_register(reg, val)
        time.sleep(0.003)

    print("[+] CC1101 configured.")
    return True

def send_burst():
    pattern = [0xAA, 0x55] * 30  # 60-byte alternating pattern
    payload = [len(pattern)] + pattern

    spi.transfer([0x36])  # SIDLE
    time.sleep(0.002)
    spi.write_burst(0x3F, payload)
    time.sleep(0.002)
    spi.transfer([0x35])  # STX

    print("[>] Packet sent")
    for i in range(10):
        gdo = spi.read_gdo0()
        print(f"  GDO0[{i}] = {gdo}")
        time.sleep(0.01)

try:
    if setup_cc1101():
        print("[*] Transmitting 10 bursts...")
        for i in range(10):
            print(f"[*] Burst {i+1}/10")
            send_burst()
            time.sleep(0.5)
    else:
        print("[!] Setup failed.")

except KeyboardInterrupt:
    print("[!] Interrupted.")

finally:
    spi.cleanup()

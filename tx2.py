# tx_loop_easy.py
import time
from cc1101_conf import SoftwareSPI  # make sure this class is in your project

spi = SoftwareSPI()

def setup_cc1101():
    print("[*] Sending RESET strobe (0x30)")
    spi.transfer([0x30])  # SRES
    time.sleep(0.1)

    print("[*] Reading version register (0x0D)")
    version = spi.transfer([0x8D, 0x00])  # Read VERSION
    print("[+] Version Register Response:", version)

    if version[1] in [0x14, 0x1E, 0x0F]:
        print("[✓] CC1101 version OK:", hex(version[1]))
    else:
        print("[!] Invalid version response, check wiring.")
        return

    print("[*] Writing basic config...")
    config = {
        0x00: 0x06,  # IOCFG2 – GDO2 output pin config
        0x02: 0x06,  # FREQ2
        0x03: 0x21,  # FREQ1
        0x04: 0x65,  # FREQ0 = 433.92 MHz
        0x05: 0x05,  # MDMCFG4 – 60 kHz BW
        0x06: 0xF8,  # MDMCFG3 – 4800 baud
        0x07: 0x03,  # MDMCFG2 – ASK/OOK, no preamble/sync
        0x08: 0x00,  # MDMCFG1 – no FEC
        0x09: 0x00,  # MDMCFG0
        0x0B: 0x06,  # CHANNR
        0x0D: 0x34,  # FSCTRL1
        0x0E: 0x0C,  # FSCTRL0
        0x10: 0x45,  # DEVIATN
        0x14: 0x18,  # MCSM2
        0x15: 0x18,  # MCSM1 – stay in TX
        0x16: 0x1D,  # MCSM0
        0x17: 0x30,  # PKTLEN
        0x18: 0x04,  # PKTCTRL1
        0x19: 0x05,  # PKTCTRL0
    }

    for reg, val in config.items():
        spi.write_register(reg, val)
        time.sleep(0.005)

    print("[+] CC1101 configured.")

# def send_burst():
#     print("[*] Sending TX burst...")

#     # Make sure CC1101 is in IDLE before writing FIFO
#     spi.transfer([0x36])  # SIDLE
#     time.sleep(0.01)

#     # Payload (4 bytes of pattern)
#     packet = [0xAA, 0x55, 0xAA, 0x55]
#     spi.write_burst(0x3F, packet)  # Write to TX FIFO
#     time.sleep(0.005)

#     spi.transfer([0x35])  # STX - start transmission
#     print("[+] STX strobe sent")

#     # Optional: check GDO0
#     print("  GDO0:", spi.read_gdo0())
#     print("[>] Packet sent.\n")
#     time.sleep(0.2)

def send_long_burst():
    print("[*] Sending long repetitive bursts...")

    pattern = [0xAA, 0x55] * 30  # 60 bytes (max for TX FIFO)
    fifo_payload = [len(pattern)] + pattern  # First byte = length

    for burst in range(10):  # Repeat 10 times for longer signal
        spi.transfer([0x36])  # SIDLE
        time.sleep(0.002)

        spi.write_burst(0x3F, fifo_payload)
        time.sleep(0.002)

        spi.transfer([0x35])  # STX
        print(f"[>] Burst {burst + 1}/10 sent")

        # Optional: check GDO0 status
        for i in range(5):
            print(f"  GDO0[{i}]:", spi.read_gdo0())
            time.sleep(0.005)

try:
    setup_cc1101()
    print("[*] Starting TX loop (every 0.5s)...")
    while True:
        send_burst()
        time.sleep(0.5)

except KeyboardInterrupt:
    print("[!] Stopped by user.")

finally:
    spi.cleanup()

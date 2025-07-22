# cc1101_tx_test.py

import time
import RPi.GPIO as GPIO

class SoftwareSPI:
    def __init__(self, sck=21, mosi=20, miso=19, csn=18, gdo0=26, gdo2=16):
        self.SCK = sck
        self.MOSI = mosi
        self.MISO = miso
        self.CSN = csn
        self.GDO0 = gdo0
        self.GDO2 = gdo2

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.SCK, GPIO.OUT)
        GPIO.setup(self.MOSI, GPIO.OUT)
        GPIO.setup(self.MISO, GPIO.IN)
        GPIO.setup(self.CSN, GPIO.OUT)
        GPIO.setup(self.GDO0, GPIO.IN)
        GPIO.setup(self.GDO2, GPIO.IN)
        GPIO.output(self.SCK, GPIO.LOW)
        GPIO.output(self.MOSI, GPIO.LOW)
        GPIO.output(self.CSN, GPIO.HIGH)

    def transfer(self, data):
        GPIO.output(self.CSN, GPIO.LOW)
        time.sleep(0.001)
        result = []
        for byte in data:
            received = 0
            for i in range(8):
                bit_out = (byte >> (7 - i)) & 1
                GPIO.output(self.MOSI, bit_out)
                GPIO.output(self.SCK, GPIO.HIGH)
                time.sleep(0.00001)
                bit_in = GPIO.input(self.MISO)
                received |= (bit_in << (7 - i))
                GPIO.output(self.SCK, GPIO.LOW)
                time.sleep(0.00001)
            result.append(received)
        GPIO.output(self.CSN, GPIO.HIGH)
        return result

    def write_register(self, addr, value):
        self.transfer([addr, value])

    def write_burst(self, addr, values):
        self.transfer([addr | 0x40] + values)

    def read_gdo0(self):
        return GPIO.input(self.GDO0)

    def cleanup(self):
        GPIO.cleanup()

spi = SoftwareSPI()

def setup_cc1101():
    print("[*] Resetting CC1101...")
    spi.transfer([0x30])
    time.sleep(0.1)

    print("[*] Configuring GDO0 to show TX status...")
    spi.write_register(0x00, 0x06)  # IOCFG0 = 0x06: Assert HIGH when TX

    # Minimal necessary config
    config = {
        0x02: 0x06, 0x03: 0x21, 0x04: 0x65,  # FREQ2/1/0 = 433.92 MHz
        0x07: 0x00,                         # MDMCFG2: no sync word
        0x0B: 0x06,                         # CHANNR
        0x10: 0x45,                         # MDMCFG4
        0x14: 0x18,                         # MCSM2
        0x15: 0x18,                         # MCSM1
        0x17: 0x04,                         # PKTLEN
        0x19: 0x05,                         # PKTCTRL0
    }
    for reg, val in config.items():
        spi.write_register(reg, val)
        time.sleep(0.005)
    print("[+] CC1101 configured")

def send_packet():
    spi.transfer([0x36])  # SIDLE
    time.sleep(0.01)
    spi.write_burst(0x3F, [0x04, 0xAA, 0x55, 0xAA, 0x55])
    time.sleep(0.01)
    spi.transfer([0x35])  # STX

    print("[>] Sent packet. Reading GDO0:")
    for i in range(10):
        print(f"GDO0[{i}]:", spi.read_gdo0())
        time.sleep(0.05)

try:
    setup_cc1101()
    while True:
        send_packet()
        time.sleep(1)

except KeyboardInterrupt:
    print("Stopped.")
    spi.cleanup()

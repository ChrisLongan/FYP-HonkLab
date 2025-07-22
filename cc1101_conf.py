# softwarespi.py
import RPi.GPIO as GPIO
import time

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

        # Setup SPI lines
        GPIO.setup(self.SCK, GPIO.OUT)
        GPIO.setup(self.MOSI, GPIO.OUT)
        GPIO.setup(self.MISO, GPIO.IN)
        GPIO.setup(self.CSN, GPIO.OUT)

        # Setup GDO lines
        GPIO.setup(self.GDO0, GPIO.IN)
        GPIO.setup(self.GDO2, GPIO.IN)

        # Initialize lines
        GPIO.output(self.SCK, GPIO.LOW)
        GPIO.output(self.MOSI, GPIO.LOW)
        GPIO.output(self.CSN, GPIO.HIGH)

    # def transfer(self, data):
    #     """Transfer a list of bytes and return the response from MISO."""
    #     result = []
    #     GPIO.output(self.CSN, GPIO.LOW)
    #     time.sleep(0.001)

    #     for byte in data:
    #         received = 0
    #         for i in range(8):
    #             bit_out = (byte >> (7 - i)) & 1
    #             GPIO.output(self.MOSI, bit_out)
    #             GPIO.output(self.SCK, GPIO.HIGH)
    #             time.sleep(0.00001)

    #             bit_in = GPIO.input(self.MISO)
    #             received |= (bit_in << (7 - i))

    #             GPIO.output(self.SCK, GPIO.LOW)
    #             time.sleep(0.00001)

    #         result.append(received)

    #     GPIO.output(self.CSN, GPIO.HIGH)
    #     return result

    def transfer(self, data):
        result = []

        print("[DEBUG] Pulling CSN LOW")
        GPIO.output(self.CSN, GPIO.LOW)
        time.sleep(0.001)

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

        print("[DEBUG] Pulling CSN HIGH")
        GPIO.output(self.CSN, GPIO.HIGH)
        return result

    def read_gdo0(self):
        return GPIO.input(self.GDO0)

    def read_gdo2(self):
        return GPIO.input(self.GDO2)

    def cleanup(self):
        GPIO.cleanup()

    def write_register(self, address, value):
        """Write a single byte to a CC1101 register."""
        self.transfer([address, value])

    def write_burst(self, address, values):
        """Write multiple bytes starting at a register address (burst mode)."""
        self.transfer([address | 0x40] + values)

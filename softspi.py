import RPi.GPIO as GPIO
import time

class CC1101:
    def __init__(self, sck, mosi, miso, csn, gdo0, gdo2):
        self.SCK = sck
        self.MOSI = mosi
        self.MISO = miso
        self.CSN = csn
        self.GDO0 = gdo0
        self.GDO2 = gdo2

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # SPI lines
        GPIO.setup(self.SCK, GPIO.OUT)
        GPIO.setup(self.MOSI, GPIO.OUT)
        GPIO.setup(self.MISO, GPIO.IN)
        GPIO.setup(self.CSN, GPIO.OUT)

        # GDO lines
        GPIO.setup(self.GDO0, GPIO.IN)
        GPIO.setup(self.GDO2, GPIO.IN)

        GPIO.output(self.SCK, GPIO.LOW)
        GPIO.output(self.MOSI, GPIO.LOW)
        GPIO.output(self.CSN, GPIO.HIGH)

    def spi_write(self, byte):
        for i in range(8):
            GPIO.output(self.SCK, GPIO.LOW)
            GPIO.output(self.MOSI, (byte & (1 << (7 - i))) != 0)
            GPIO.output(self.SCK, GPIO.HIGH)
        GPIO.output(self.SCK, GPIO.LOW)

    def spi_read(self):
        value = 0
        for i in range(8):
            GPIO.output(self.SCK, GPIO.HIGH)
            if GPIO.input(self.MISO):
                value |= (1 << (7 - i))
            GPIO.output(self.SCK, GPIO.LOW)
        return value

    def write_register(self, addr, value):
        GPIO.output(self.CSN, GPIO.LOW)
        self.spi_write(addr)
        self.spi_write(value)
        GPIO.output(self.CSN, GPIO.HIGH)

    def read_register(self, addr):
        GPIO.output(self.CSN, GPIO.LOW)
        self.spi_write(addr | 0x80)  # Read flag
        val = self.spi_read()
        GPIO.output(self.CSN, GPIO.HIGH)
        return val

    def send_strobe(self, strobe):
        GPIO.output(self.CSN, GPIO.LOW)
        self.spi_write(strobe)
        GPIO.output(self.CSN, GPIO.HIGH)

    def reset(self):
        GPIO.output(self.CSN, GPIO.HIGH)
        time.sleep(0.01)
        GPIO.output(self.CSN, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(self.CSN, GPIO.HIGH)
        time.sleep(0.045)
        GPIO.output(self.CSN, GPIO.LOW)
        self.spi_write(0x30)  # SRES
        GPIO.output(self.CSN, GPIO.HIGH)

    def init(self):
        self.write_register(0x0B, 0x06)  # FSCTRL1
        self.write_register(0x0D, 0x21)  # FREQ2
        self.write_register(0x0E, 0xB0)  # FREQ1
        self.write_register(0x0F, 0x6A)  # FREQ0
        self.write_register(0x10, 0xF5)  # MDMCFG4
        self.write_register(0x11, 0x83)  # MDMCFG3
        self.write_register(0x12, 0x13)  # MDMCFG2
        self.write_register(0x15, 0x34)  # DEVIATN
        self.write_register(0x18, 0x16)  # MCSM0
        self.write_register(0x19, 0x1D)  # FOCCFG
        self.write_register(0x1C, 0xC7)  # AGCCTRL2
        self.write_register(0x1D, 0x00)  # AGCCTRL1
        self.write_register(0x1E, 0xB0)  # AGCCTRL0
        self.write_register(0x21, 0xB6)  # FREND1
        self.write_register(0x22, 0x10)  # FREND0
        self.write_register(0x23, 0xEA)  # FSCAL3
        self.write_register(0x24, 0x2A)  # FSCAL2
        self.write_register(0x25, 0x00)  # FSCAL1
        self.write_register(0x26, 0x1F)  # FSCAL0

        # GDO0: assert during TX (sync word sent)
        self.write_register(0x02, 0x06)

    def set_frequency(self, freq_mhz):
        f = int((freq_mhz * 1000000.0) / (26.0e6 / (1 << 16)))
        self.write_register(0x0D, (f >> 16) & 0xFF)
        self.write_register(0x0E, (f >> 8) & 0xFF)
        self.write_register(0x0F, f & 0xFF)

    def set_modulation(self, mod):
        if mod == 'ASK_OOK':
            self.write_register(0x12, 0x30)
        elif mod == '2-FSK':
            self.write_register(0x12, 0x10)

    def set_power_level(self, level):
        table = [0xC0, 0xC3, 0xC6, 0xC9, 0xCC, 0xCF, 0x12, 0x03]  # PA table
        self.write_register(0x3E, table[level])

    def send_data(self, data):
        self.send_strobe(0x3B)  # SFTX - flush TX FIFO
        time.sleep(0.001)

        GPIO.output(self.CSN, GPIO.LOW)
        self.spi_write(0x7F)  # TX FIFO burst
        for byte in data:
            self.spi_write(byte)
        GPIO.output(self.CSN, GPIO.HIGH)

        self.send_strobe(0x35)  # STX
        time.sleep(0.05)        # allow TX time
        self.send_strobe(0x36)  # SIDLE

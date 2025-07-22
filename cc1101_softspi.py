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

        GPIO.setup(self.SCK, GPIO.OUT)
        GPIO.setup(self.MOSI, GPIO.OUT)
        GPIO.setup(self.MISO, GPIO.IN)
        GPIO.setup(self.CSN, GPIO.OUT)
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
        self.spi_write(addr | 0x80)
        val = self.spi_read()
        GPIO.output(self.CSN, GPIO.HIGH)
        return val

    def send_strobe(self, strobe):
        GPIO.output(self.CSN, GPIO.LOW)
        self.spi_write(strobe)
        status = self.spi_read()
        GPIO.output(self.CSN, GPIO.HIGH)
        print(f"[DEBUG] STROBE 0x{strobe:02X} → status byte: 0x{status:02X}")
        return status

    def get_marc_state(self):
        state = self.read_register(0x35) & 0x1F
        print(f"[DEBUG] MARCSTATE: 0x{state:02X}")
        return state

    def reset(self):
        GPIO.output(self.CSN, GPIO.HIGH)
        time.sleep(0.01)
        GPIO.output(self.CSN, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(self.CSN, GPIO.HIGH)
        time.sleep(0.045)
        GPIO.output(self.CSN, GPIO.LOW)
        self.spi_write(0x30)
        GPIO.output(self.CSN, GPIO.HIGH)

    def init(self):
        self.write_register(0x0B, 0x06)
        self.write_register(0x0D, 0x21)
        self.write_register(0x0E, 0xB0)
        self.write_register(0x0F, 0x6A)
        self.write_register(0x10, 0xF5)
        self.write_register(0x11, 0x83)
        self.write_register(0x12, 0x13)
        self.write_register(0x15, 0x34)
        self.write_register(0x18, 0x16)
        self.write_register(0x19, 0x1D)
        self.write_register(0x1C, 0xC7)
        self.write_register(0x1D, 0x00)
        self.write_register(0x1E, 0xB0)
        self.write_register(0x21, 0xB6)
        self.write_register(0x22, 0x10)
        self.write_register(0x23, 0xEA)
        self.write_register(0x24, 0x2A)
        self.write_register(0x25, 0x00)
        self.write_register(0x26, 0x1F)
        self.write_register(0x02, 0x06)
        print(f"[DEBUG] IOCFG0 (GDO0 config) = 0x{self.read_register(0x02):02X}")

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
        table = [0xC0, 0xC3, 0xC6, 0xC9, 0xCC, 0xCF, 0x12, 0x03]
        GPIO.output(self.CSN, GPIO.LOW)
        self.spi_write(0x7E)
        self.spi_write(table[level])
        GPIO.output(self.CSN, GPIO.HIGH)
        time.sleep(0.01)
        print(f"[DEBUG] PATABLE loaded with: 0x{table[level]:02X}")

    def spi_write_burst(self, addr, data):
        GPIO.output(self.CSN, GPIO.LOW)
        self.spi_write(addr | 0x40)  # burst write
        for byte in data:
            self.spi_write(byte)
        GPIO.output(self.CSN, GPIO.HIGH)

    def send_data(self, data):
        self.send_strobe(0x36)  # SIDLE
        time.sleep(0.01)
        self.send_strobe(0x3A)  # SFTX
        time.sleep(0.01)

        retries = 1
        for attempt in range(retries + 1):
            self.spi_write_burst(0x3F, data)
            self.send_strobe(0x35)  # STX
            time.sleep(0.05)

            marcstate = self.get_marc_state()
            if marcstate in (0x00, 0x1F):
                print(f"[WARN] TX failed (MARCSTATE={hex(marcstate)}). Attempt {attempt + 1} of {retries + 1}")
                if attempt < retries:
                    print("[INFO] Resetting radio...")
                    self.reset()
                    self.init()
                    self.set_frequency(433.92)
                    self.set_modulation("ASK_OOK")
                    self.set_power_level(0)
                    time.sleep(0.05)
                    continue
                else:
                    print("[ERROR] TX failed after retry. Aborting.\n")
                    return
            else:
                break

        gdo0_state = GPIO.input(self.GDO0)
        print(f"[DEBUG] GDO0 state after TX: {gdo0_state}")

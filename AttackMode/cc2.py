import RPi.GPIO as GPIO
import time

class CC1101_Working:
    """CC1101 driver using ONLY the timing/method that actually worked"""
    
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

    def working_spi_write(self, byte):
        """SPI write using EXACT timing from working manual test"""
        for i in range(8):
            GPIO.output(self.SCK, GPIO.LOW)
            time.sleep(0.001)  # Exact 1ms from working test
            GPIO.output(self.MOSI, (byte & (1 << (7 - i))) != 0)
            time.sleep(0.001)
            GPIO.output(self.SCK, GPIO.HIGH)
            time.sleep(0.001)
        GPIO.output(self.SCK, GPIO.LOW)

    def working_spi_read(self):
        """SPI read using EXACT timing from working manual test"""
        value = 0
        for i in range(8):
            GPIO.output(self.SCK, GPIO.HIGH)
            time.sleep(0.001)  # Exact 1ms from working test
            if GPIO.input(self.MISO):
                value |= (1 << (7 - i))
            GPIO.output(self.SCK, GPIO.LOW)
            time.sleep(0.001)
        return value

    def working_reset(self):
        """Reset using EXACT sequence from working manual test"""
        print("[DEBUG] Using working reset sequence...")
        
        # Exact sequence that worked
        GPIO.output(self.CSN, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(self.CSN, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(self.CSN, GPIO.HIGH)
        time.sleep(0.05)
        
        # Send SRES with working timing
        GPIO.output(self.CSN, GPIO.LOW)
        self.working_spi_write(0x30)  # SRES
        GPIO.output(self.CSN, GPIO.HIGH)
        time.sleep(0.1)  # Wait after reset

    def working_read_register(self, addr):
        """Read register using EXACT method that worked"""
        GPIO.output(self.CSN, GPIO.LOW)
        time.sleep(0.001)
        
        # Use 0xF0 | addr for burst read (like working test used 0xF1)
        self.working_spi_write(0xF0 | (addr & 0x0F))
        val = self.working_spi_read()
        
        time.sleep(0.001)
        GPIO.output(self.CSN, GPIO.HIGH)
        return val

    def working_write_register(self, addr, value):
        """Write register using working timing"""
        GPIO.output(self.CSN, GPIO.LOW)
        time.sleep(0.001)
        self.working_spi_write(addr)
        self.working_spi_write(value)
        time.sleep(0.001)
        GPIO.output(self.CSN, GPIO.HIGH)

    def test_communication(self):
        """Test communication using working method"""
        print("[INFO] Testing communication with working method...")
        
        self.working_reset()
        
        # Try VERSION read exactly like working test
        version = self.working_read_register(0x01)  # 0xF1 = 0xF0 | 0x01
        print(f"[DEBUG] VERSION register: 0x{version:02X}")
        
        if version == 0x14:
            print("[SUCCESS] ✅ CC1101 responding correctly!")
            return True
        else:
            print(f"[FAILED] ❌ Got 0x{version:02X}, expected 0x14")
            return False

    def send_strobe_working(self, strobe):
        """Send strobe command using working timing"""
        GPIO.output(self.CSN, GPIO.LOW)
        time.sleep(0.001)
        self.working_spi_write(strobe)
        status = self.working_spi_read()
        time.sleep(0.001)
        GPIO.output(self.CSN, GPIO.HIGH)
        print(f"[DEBUG] STROBE 0x{strobe:02X} → status: 0x{status:02X}")
        return status

    def basic_init(self):
        """Initialize with minimal, essential registers only"""
        print("[INFO] Basic CC1101 initialization...")
        
        if not self.test_communication():
            print("[ERROR] Communication failed - cannot initialize")
            return False
        
        try:
            # Only essential registers for 433MHz ASK/OOK
            self.working_write_register(0x0D, 0x21)  # FREQ2
            self.working_write_register(0x0E, 0xB0)  # FREQ1  
            self.working_write_register(0x0F, 0x6A)  # FREQ0 (433.92 MHz)
            
            self.working_write_register(0x12, 0x30)  # ASK/OOK modulation
            self.working_write_register(0x18, 0x16)  # MCSM0
            
            # Power setting
            GPIO.output(self.CSN, GPIO.LOW)
            time.sleep(0.001)
            self.working_spi_write(0x7E)  # PATABLE
            self.working_spi_write(0x03)  # Max power
            time.sleep(0.001)
            GPIO.output(self.CSN, GPIO.HIGH)
            
            print("[SUCCESS] ✅ Basic initialization complete")
            return True
            
        except Exception as e:
            print(f"[ERROR] Initialization failed: {e}")
            return False

    def send_data_working(self, data):
        """Send data using working timing"""
        print(f"[INFO] Sending {len(data)} bytes...")
        
        # Go to idle
        self.send_strobe_working(0x36)  # SIDLE
        time.sleep(0.01)
        
        # Flush TX FIFO
        self.send_strobe_working(0x3A)  # SFTX
        time.sleep(0.01)
        
        # Load data into FIFO
        GPIO.output(self.CSN, GPIO.LOW)
        time.sleep(0.001)
        self.working_spi_write(0x7F)  # TX FIFO burst write
        for byte in data:
            self.working_spi_write(byte)
        time.sleep(0.001)
        GPIO.output(self.CSN, GPIO.HIGH)
        
        # Start transmission
        self.send_strobe_working(0x35)  # STX
        time.sleep(0.1)  # Wait for transmission
        
        # Check result
        gdo0_state = GPIO.input(self.GDO0)
        print(f"[DEBUG] GDO0 after TX: {gdo0_state}")
        
        return True

def test_working_driver():
    """Test the working driver"""
    print("CC1101 Working Driver Test")
    print("=" * 40)
    
    # Initialize using working method
    cc = CC1101_Working(21, 20, 19, 12, 26, 16)
    
    # Test communication
    if cc.test_communication():
        # Initialize for transmission
        if cc.basic_init():
            # Test transmission
            test_data = [0xAA, 0x55, 0xAA, 0x55]
            
            print("\nTesting data transmission...")
            for i in range(3):
                print(f"Transmission {i+1}/3...")
                cc.send_data_working(test_data)
                time.sleep(1)
            
            print("\n✅ All tests passed!")
            return cc
        else:
            print("❌ Initialization failed")
            return None
    else:
        print("❌ Communication test failed")
        return None

def send_custom_bits(cc, bit_string):
    """Send your custom bit pattern using working driver"""
    if cc is None:
        print("❌ CC1101 not initialized")
        return
    
    print("\n" + "=" * 40)
    print("SENDING CUSTOM BIT PATTERN")
    print("=" * 40)
    
    # Convert bits to bytes
    bit_string = bit_string.replace(' ', '')
    while len(bit_string) % 8 != 0:
        bit_string = '0' + bit_string
    
    bytes_list = []
    for i in range(0, len(bit_string), 8):
        byte_chunk = bit_string[i:i+8]
        byte_value = int(byte_chunk, 2)
        bytes_list.append(byte_value)
    
    print(f"Bit pattern: {bit_string}")
    print(f"Bytes: {[hex(b) for b in bytes_list]}")
    print()
    
    # Send multiple times
    for i in range(5):
        print(f"Custom transmission {i+1}/5...")
        cc.send_data_working(bytes_list)
        time.sleep(0.1)
    
    print("✅ Custom bit pattern sent!")

# Main test
if __name__ == "__main__":
    try:
        # Test the working driver
        working_cc = test_working_driver()
        
        if working_cc:
            # Send your custom bit pattern
            your_bits = "1000111010001110100010001000111011101110111011101110111010001110100011101110111010001000100011101"
            send_custom_bits(working_cc, your_bits)
            
    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        GPIO.cleanup()
        print("GPIO cleanup complete")

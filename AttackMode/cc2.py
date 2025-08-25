import RPi.GPIO as GPIO
import time

class CC1101_Hybrid:
    """
    Hybrid CC1101 driver:
    - Uses working communication timing from manual test
    - Uses proper RF configuration that actually transmits
    """
    
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
        """Working SPI write timing"""
        for i in range(8):
            GPIO.output(self.SCK, GPIO.LOW)
            time.sleep(0.001)
            GPIO.output(self.MOSI, (byte & (1 << (7 - i))) != 0)
            time.sleep(0.001)
            GPIO.output(self.SCK, GPIO.HIGH)
            time.sleep(0.001)
        GPIO.output(self.SCK, GPIO.LOW)

    def spi_read(self):
        """Working SPI read timing"""
        value = 0
        for i in range(8):
            GPIO.output(self.SCK, GPIO.HIGH)
            time.sleep(0.001)
            if GPIO.input(self.MISO):
                value |= (1 << (7 - i))
            GPIO.output(self.SCK, GPIO.LOW)
            time.sleep(0.001)
        return value

    def write_register(self, addr, value):
        """Write register using working timing"""
        GPIO.output(self.CSN, GPIO.LOW)
        time.sleep(0.001)
        self.spi_write(addr)
        self.spi_write(value)
        time.sleep(0.001)
        GPIO.output(self.CSN, GPIO.HIGH)

    def read_register(self, addr):
        """Read register using working timing"""
        GPIO.output(self.CSN, GPIO.LOW)
        time.sleep(0.001)
        self.spi_write(addr | 0x80)
        val = self.spi_read()
        time.sleep(0.001)
        GPIO.output(self.CSN, GPIO.HIGH)
        return val

    def send_strobe(self, strobe):
        """Send strobe with working timing"""
        GPIO.output(self.CSN, GPIO.LOW)
        time.sleep(0.001)
        self.spi_write(strobe)
        status = self.spi_read()
        time.sleep(0.001)
        GPIO.output(self.CSN, GPIO.HIGH)
        print(f"[DEBUG] STROBE 0x{strobe:02X} → status: 0x{status:02X}")
        return status

    def reset(self):
        """Working reset sequence"""
        print("[DEBUG] Resetting CC1101...")
        GPIO.output(self.CSN, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(self.CSN, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(self.CSN, GPIO.HIGH)
        time.sleep(0.05)
        
        GPIO.output(self.CSN, GPIO.LOW)
        time.sleep(0.001)
        self.spi_write(0x30)  # SRES
        time.sleep(0.001)
        GPIO.output(self.CSN, GPIO.HIGH)
        time.sleep(0.1)

    def get_marc_state(self):
        """Get radio state"""
        state = self.read_register(0x35) & 0x1F
        print(f"[DEBUG] MARCSTATE: 0x{state:02X}")
        return state

    def init_for_transmission(self):
        """Initialize with PROPER RF configuration for transmission"""
        print("[INFO] Initializing CC1101 for RF transmission...")
        
        # Test communication first
        version = self.read_register(0x31)
        print(f"[DEBUG] VERSION: 0x{version:02X}")
        
        if version != 0x14:
            print(f"[ERROR] Communication failed - VERSION should be 0x14, got 0x{version:02X}")
            return False
        
        # WORKING RF CONFIGURATION (from original working code)
        print("[DEBUG] Loading RF configuration...")
        
        # Core RF registers - THESE MADE YOUR ORIGINAL CODE WORK
        self.write_register(0x0B, 0x06)  # FSCTRL1
        self.write_register(0x0D, 0x21)  # FREQ2 
        self.write_register(0x0E, 0xB0)  # FREQ1
        self.write_register(0x0F, 0x6A)  # FREQ0 - 433.92 MHz
        self.write_register(0x10, 0xF5)  # MDMCFG4 
        self.write_register(0x11, 0x83)  # MDMCFG3
        self.write_register(0x12, 0x13)  # MDMCFG2 - Original working modulation!
        self.write_register(0x15, 0x34)  # MDMCFG0
        self.write_register(0x18, 0x16)  # MCSM0
        self.write_register(0x19, 0x1D)  # MCSM1
        self.write_register(0x1C, 0xC7)  # FREND1
        self.write_register(0x1D, 0x00)  # FREND0  
        self.write_register(0x1E, 0xB0)  # FSCAL3
        self.write_register(0x21, 0xB6)  # FSCAL2
        self.write_register(0x22, 0x10)  # FSCAL1
        self.write_register(0x23, 0xEA)  # FSCAL0
        self.write_register(0x24, 0x2A)  # FSTEST
        self.write_register(0x25, 0x00)  # TEST2
        self.write_register(0x26, 0x1F)  # TEST1
        self.write_register(0x02, 0x06)  # IOCFG0 (GDO0 config)
        
        # NOW set ASK/OOK modulation (after all other settings)
        self.write_register(0x12, 0x30)  # Change to ASK/OOK
        
        # Power amplifier table - MAXIMUM POWER
        print("[DEBUG] Setting maximum power...")
        GPIO.output(self.CSN, GPIO.LOW)
        time.sleep(0.001)
        self.spi_write(0x7E)  # PATABLE address
        self.spi_write(0xFF)  # MAXIMUM power (not 0x03!)
        time.sleep(0.001)
        GPIO.output(self.CSN, GPIO.HIGH)
        time.sleep(0.01)
        
        print("[SUCCESS] ✅ RF configuration loaded")
        return True

    def send_data(self, data):
        """Send data with proper error checking"""
        print(f"[INFO] Transmitting {len(data)} bytes...")
        
        # Go to idle first
        self.send_strobe(0x36)  # SIDLE
        time.sleep(0.01)
        
        # Flush TX FIFO  
        self.send_strobe(0x3A)  # SFTX
        time.sleep(0.01)

        # Load data into TX FIFO
        print("[DEBUG] Loading data into TX FIFO...")
        GPIO.output(self.CSN, GPIO.LOW)
        time.sleep(0.001)
        self.spi_write(0x3F | 0x40)  # TX FIFO burst write (0x7F)
        for byte in data:
            self.spi_write(byte)
        time.sleep(0.001)
        GPIO.output(self.CSN, GPIO.HIGH)
        
        # Start transmission
        print("[DEBUG] Starting transmission...")
        self.send_strobe(0x35)  # STX
        time.sleep(0.1)  # Wait for transmission to complete
        
        # Check final state
        marc_state = self.get_marc_state()
        gdo0_state = GPIO.input(self.GDO0)
        print(f"[DEBUG] Final MARCSTATE: 0x{marc_state:02X}, GDO0: {gdo0_state}")
        
        if marc_state == 0x13:  # TX state
            print("[INFO] ✅ Still transmitting...")
        elif marc_state == 0x01:  # IDLE state  
            print("[INFO] ✅ Transmission completed, returned to IDLE")
        else:
            print(f"[WARN] Unexpected final state: 0x{marc_state:02X}")
        
        return True

def test_transmission_power():
    """Test with different power levels to ensure visibility on SDR"""
    print("CC1101 Transmission Power Test")
    print("=" * 40)
    
    cc = CC1101_Hybrid(21, 20, 19, 12, 26, 16)
    
    # Reset and initialize
    cc.reset()
    
    if not cc.init_for_transmission():
        print("❌ Initialization failed")
        return None
    
    # Test with different power levels
    power_levels = [0xFF, 0xC0, 0x84, 0x60, 0x34, 0x1D, 0x0E, 0x12]
    test_data = [0xAA, 0x55, 0xAA, 0x55, 0xFF, 0x00, 0xFF, 0x00]
    
    for i, power in enumerate(power_levels):
        print(f"\n--- Testing Power Level {i+1}/8: 0x{power:02X} ---")
        
        # Set power level
        GPIO.output(cc.CSN, GPIO.LOW)
        time.sleep(0.001)
        cc.spi_write(0x7E)  # PATABLE
        cc.spi_write(power)
        time.sleep(0.001)
        GPIO.output(cc.CSN, GPIO.HIGH)
        time.sleep(0.01)
        
        # Transmit
        print(f"[SDR] *** LOOK FOR SIGNAL NOW - Power 0x{power:02X} ***")
        cc.send_data(test_data)
        
        # Long pause between power levels
        print("[INFO] Waiting 3 seconds...")
        time.sleep(3)
    
    return cc

def send_custom_pattern(cc):
    """Send your custom bit pattern"""
    if cc is None:
        print("❌ CC1101 not initialized")
        return
    
    print("\n" + "=" * 50)
    print("TRANSMITTING YOUR CUSTOM BIT PATTERN")
    print("=" * 50)
    
    # Your bit pattern
    your_bits = "1000111010001110100010001000111011101110111011101110111010001110100011101110111010001000100011101"
    
    # Convert to bytes
    padded_bits = your_bits
    while len(padded_bits) % 8 != 0:
        padded_bits = '0' + padded_bits
    
    bytes_list = []
    for i in range(0, len(padded_bits), 8):
        byte_chunk = padded_bits[i:i+8]
        byte_value = int(byte_chunk, 2)
        bytes_list.append(byte_value)
    
    print(f"Original bits: {your_bits}")
    print(f"Padded bits:  {padded_bits}")
    print(f"Bytes ({len(bytes_list)}): {[hex(b) for b in bytes_list]}")
    print()
    
    # Set maximum power for your custom signal
    GPIO.output(cc.CSN, GPIO.LOW)
    time.sleep(0.001)
    cc.spi_write(0x7E)
    cc.spi_write(0xFF)  # Maximum power
    time.sleep(0.001)
    GPIO.output(cc.CSN, GPIO.HIGH)
    
    # Transmit your pattern multiple times
    for i in range(10):
        print(f"[SDR] *** Custom Pattern Transmission {i+1}/10 ***")
        cc.send_data(bytes_list)
        time.sleep(0.5)  # 500ms between transmissions
    
    print("✅ Custom pattern transmission complete!")

# Main test
if __name__ == "__main__":
    try:
        print("🔴 PREPARE YOUR SDR - SCANNING 433.92 MHz")
        print("Looking for strong signals in the next 30 seconds...")
        print()
        
        # Test different power levels first
        working_cc = test_transmission_power()
        
        if working_cc:
            print("\n🔴 SDR CHECK: Did you see ANY signals above?")
            input("Press ENTER when ready to send your custom pattern...")
            
            # Send your custom bit pattern
            send_custom_pattern(working_cc)
        
    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        GPIO.cleanup()
        print("GPIO cleanup complete")

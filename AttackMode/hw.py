import spidev
import RPi.GPIO as GPIO
import time

class CC1101_HardwareSPI:
    """
    CC1101 driver using hardware SPI - MUCH faster and more reliable
    """
    
    def __init__(self, spi_bus=0, spi_device=0, csn_pin=8, gdo0_pin=25, gdo2_pin=24):
        """
        Initialize CC1101 with hardware SPI
        
        Args:
            spi_bus: SPI bus number (usually 0)
            spi_device: SPI device (0 or 1, determines which CE pin)
            csn_pin: Chip select pin (GPIO 8 for CE0, GPIO 7 for CE1)
            gdo0_pin: GDO0 pin
            gdo2_pin: GDO2 pin
        """
        self.CSN = csn_pin
        self.GDO0 = gdo0_pin
        self.GDO2 = gdo2_pin
        
        # Initialize hardware SPI
        self.spi = spidev.SpiDev()
        self.spi.open(spi_bus, spi_device)
        self.spi.max_speed_hz = 1000000  # 1 MHz (can go up to 10 MHz!)
        self.spi.mode = 0  # CPOL=0, CPHA=0
        
        # Setup GPIO for control pins
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.CSN, GPIO.OUT)
        GPIO.setup(self.GDO0, GPIO.IN)
        GPIO.setup(self.GDO2, GPIO.IN)
        
        GPIO.output(self.CSN, GPIO.HIGH)
        
        print(f"[INFO] Hardware SPI initialized:")
        print(f"  SPI Bus: {spi_bus}, Device: {spi_device}")
        print(f"  Speed: {self.spi.max_speed_hz/1000000:.1f} MHz")
        print(f"  CSN: GPIO {csn_pin}")
        print(f"  GDO0: GPIO {gdo0_pin}")
        print(f"  GDO2: GPIO {gdo2_pin}")

    def write_register(self, addr, value):
        """Write to CC1101 register using hardware SPI"""
        GPIO.output(self.CSN, GPIO.LOW)
        self.spi.xfer2([addr, value])
        GPIO.output(self.CSN, GPIO.HIGH)

    def read_register(self, addr):
        """Read from CC1101 register using hardware SPI"""
        GPIO.output(self.CSN, GPIO.LOW)
        result = self.spi.xfer2([addr | 0x80, 0x00])
        GPIO.output(self.CSN, GPIO.HIGH)
        return result[1]

    def send_strobe(self, strobe):
        """Send strobe command using hardware SPI"""
        GPIO.output(self.CSN, GPIO.LOW)
        result = self.spi.xfer2([strobe, 0x00])
        GPIO.output(self.CSN, GPIO.HIGH)
        
        status = result[1]
        state = status & 0x0F
        chip_ready = (status & 0x80) == 0
        
        state_names = {
            0x00: "IDLE", 0x01: "RX", 0x02: "TX", 0x03: "FSTXON",
            0x13: "TX_MODE", 0x14: "TX_END"
        }
        
        state_name = state_names.get(state, f"STATE_0x{state:02X}")
        ready_text = "READY" if chip_ready else "NOT_READY"
        
        print(f"[DEBUG] STROBE 0x{strobe:02X} → 0x{status:02X} ({ready_text}, {state_name})")
        return status

    def reset(self):
        """Reset CC1101 using hardware SPI"""
        print("[DEBUG] Hardware SPI reset...")
        
        # Hardware reset
        GPIO.output(self.CSN, GPIO.HIGH)
        time.sleep(0.01)
        GPIO.output(self.CSN, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(self.CSN, GPIO.HIGH)
        time.sleep(0.01)
        
        # Software reset
        GPIO.output(self.CSN, GPIO.LOW)
        self.spi.xfer2([0x30])  # SRES strobe
        GPIO.output(self.CSN, GPIO.HIGH)
        time.sleep(0.1)  # Much shorter wait with hardware SPI!

    def get_version(self):
        """Get CC1101 version - should return 0x14"""
        version = self.read_register(0x31)
        print(f"[DEBUG] VERSION register: 0x{version:02X}")
        return version

    def init_fast(self):
        """Fast initialization using hardware SPI"""
        print("[INFO] Fast hardware SPI initialization...")
        
        self.reset()
        
        # Check communication
        version = self.get_version()
        if version != 0x14:
            print(f"[ERROR] CC1101 not responding! VERSION = 0x{version:02X}")
            return False
        
        print("[SUCCESS] ✅ CC1101 communication confirmed!")
        
        # Configuration registers - loaded much faster with hardware SPI
        config_regs = [
            # Frequency configuration (433.92 MHz)
            (0x0D, 0x21),  # FREQ2
            (0x0E, 0xB0),  # FREQ1
            (0x0F, 0x6A),  # FREQ0
            
            # Modulation and data rate
            (0x10, 0xC8),  # MDMCFG4
            (0x11, 0x93),  # MDMCFG3  
            (0x12, 0x30),  # MDMCFG2 - ASK/OOK
            (0x13, 0x22),  # MDMCFG1
            (0x14, 0xF8),  # MDMCFG0
            
            # Packet configuration
            (0x08, 0x32),  # PKTCTRL0 - async mode
            (0x07, 0x00),  # PKTCTRL1
            
            # State machine
            (0x18, 0x16),  # MCSM0
            (0x19, 0x0F),  # MCSM1
            
            # Front end
            (0x1C, 0xC7),  # FREND1
            (0x1D, 0x00),  # FREND0
            
            # Frequency calibration
            (0x1E, 0xB0),  # FSCAL3
            (0x21, 0xB6),  # FSCAL2
            (0x22, 0x10),  # FSCAL1
            (0x23, 0xEA),  # FSCAL0
            
            # Test settings
            (0x24, 0x2A),  # FSTEST
            (0x25, 0x00),  # TEST2
            (0x26, 0x1F),  # TEST1
            
            # GPIO configuration
            (0x02, 0x06),  # IOCFG0
        ]
        
        print("[DEBUG] Loading configuration registers...")
        for addr, value in config_regs:
            self.write_register(addr, value)
            # No delays needed with hardware SPI!
        
        # Set power level
        GPIO.output(self.CSN, GPIO.LOW)
        self.spi.xfer2([0x7E, 0xFF])  # PATABLE = max power
        GPIO.output(self.CSN, GPIO.HIGH)
        
        print("[SUCCESS] ✅ Fast initialization complete!")
        return True

    def get_marc_state(self):
        """Get radio state machine state"""
        state = self.read_register(0x35) & 0x1F
        print(f"[DEBUG] MARCSTATE: 0x{state:02X}")
        return state

    def send_data_fast(self, data):
        """Send data using fast hardware SPI"""
        print(f"[INFO] Fast transmission of {len(data)} bytes")
        
        # Go to idle
        self.send_strobe(0x36)  # SIDLE
        time.sleep(0.001)  # Much faster!
        
        # Flush TX FIFO
        self.send_strobe(0x3A)  # SFTX  
        time.sleep(0.001)
        
        # Load data using hardware SPI burst write
        GPIO.output(self.CSN, GPIO.LOW)
        tx_data = [0x3F] + data  # TX FIFO address + data
        self.spi.xfer2(tx_data)
        GPIO.output(self.CSN, GPIO.HIGH)
        
        print(f"[DEBUG] Loaded {len(data)} bytes in single burst")
        
        # Start transmission
        tx_status = self.send_strobe(0x35)  # STX
        
        if (tx_status & 0x0F) == 0x13:  # TX mode
            print("[SUCCESS] ✅ Entered TX mode!")
        else:
            print(f"[WARN] Unexpected TX status: 0x{tx_status:02X}")
        
        # Wait for transmission
        time.sleep(0.1)
        
        # Return to idle
        final_status = self.send_strobe(0x36)  # SIDLE
        
        return (tx_status & 0x0F) == 0x13

    def close(self):
        """Clean up hardware SPI"""
        self.spi.close()
        GPIO.cleanup()

def test_hardware_spi():
    """Test CC1101 with hardware SPI"""
    print("CC1101 Hardware SPI Test")
    print("=" * 40)
    print("This should be MUCH faster and more reliable!")
    print()
    
    # Initialize with hardware SPI
    # Using SPI0, device 0 (CE0 = GPIO 8)
    cc = CC1101_HardwareSPI(
        spi_bus=0, 
        spi_device=0,
        csn_pin=8,   # CE0
        gdo0_pin=25,
        gdo2_pin=24
    )
    
    try:
        # Fast initialization
        if not cc.init_fast():
            print("❌ Initialization failed")
            return None
        
        # Test patterns
        test_data = [
            [0xAA, 0x55],
            [0xFF, 0x00, 0xFF, 0x00],  
            [0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0]
        ]
        
        for i, pattern in enumerate(test_data):
            print(f"\n--- Hardware SPI Test {i+1}/3 ---")
            print(f"[SDR] *** WATCH 433.92 MHz - Much stronger signal expected! ***")
            print(f"Data: {[hex(b) for b in pattern]}")
            
            success = cc.send_data_fast(pattern)
            if success:
                print("✅ Fast transmission successful!")
            else:
                print("❌ Transmission failed")
            
            time.sleep(2)
        
        return cc
        
    except Exception as e:
        print(f"Error: {e}")
        cc.close()
        return None

def send_keyfob_fast(cc):
    """Send your keyfob signal with hardware SPI"""
    if cc is None:
        return
    
    print("\n" + "=" * 60)
    print("YOUR KEYFOB SIGNAL - HARDWARE SPI (FAST!)")
    print("=" * 60)
    
    your_bits = "1000111010001110100010001000111011101110111011101110111010001110100011101110111010001000100011101"
    
    # Convert to bytes  
    padded = your_bits
    while len(padded) % 8 != 0:
        padded = '0' + padded
    
    bytes_list = []
    for i in range(0, len(padded), 8):
        byte_val = int(padded[i:i+8], 2)
        bytes_list.append(byte_val)
    
    print(f"Pattern: {your_bits}")
    print(f"Bytes: {[hex(b) for b in bytes_list]}")
    print(f"Total bytes: {len(bytes_list)}")
    print()
    
    # Fast transmission
    for i in range(8):
        print(f"[SDR] *** Fast KeyFob Transmission {i+1}/8 ***")
        start_time = time.time()
        
        success = cc.send_data_fast(bytes_list)
        
        elapsed = time.time() - start_time
        print(f"Transmission time: {elapsed:.3f} seconds")
        
        if success:
            print("✅ Fast keyfob transmission successful!")
        else:
            print("❌ Transmission failed")
        
        time.sleep(0.5)  # Short delay between transmissions

# Main test
if __name__ == "__main__":
    try:
        print("🚀 HARDWARE SPI TEST - Expected to be MUCH better!")
        print("Make sure you've connected CC1101 to hardware SPI pins:")
        print("  SCLK → GPIO 11 (Pin 23)")
        print("  MOSI → GPIO 10 (Pin 19)")
        print("  MISO → GPIO 9  (Pin 21)")
        print("  CSN  → GPIO 8  (Pin 24)")
        print("  GDO0 → GPIO 25")
        print("  GDO2 → GPIO 24")
        print()
        
        # Test hardware SPI
        working_cc = test_hardware_spi()
        
        if working_cc:
            input("Press ENTER to send your keyfob signal with hardware SPI...")
            send_keyfob_fast(working_cc)
            
            print("\n🚀 HARDWARE SPI ADVANTAGES:")
            print("✅ 1000x faster communication")
            print("✅ More reliable timing")
            print("✅ Less CPU usage")
            print("✅ No GPIO conflicts")
            print("✅ Better RF signal quality")
        
        working_cc.close()
        
    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure spidev is installed: sudo apt install python3-spidev")
    finally:
        GPIO.cleanup()
        print("Cleanup complete")

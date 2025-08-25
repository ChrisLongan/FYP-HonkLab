import RPi.GPIO as GPIO
import time

class CC1101_FixedFIFO:
    """
    CC1101 driver with proper FIFO handling and communication recovery
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
        """Reliable SPI write with working timing"""
        for i in range(8):
            GPIO.output(self.SCK, GPIO.LOW)
            time.sleep(0.001)
            GPIO.output(self.MOSI, (byte & (1 << (7 - i))) != 0)
            time.sleep(0.001)
            GPIO.output(self.SCK, GPIO.HIGH)
            time.sleep(0.001)
        GPIO.output(self.SCK, GPIO.LOW)

    def spi_read(self):
        """Reliable SPI read with working timing"""
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
        GPIO.output(self.CSN, GPIO.LOW)
        time.sleep(0.001)
        self.spi_write(addr)
        self.spi_write(value)
        time.sleep(0.001)
        GPIO.output(self.CSN, GPIO.HIGH)

    def read_register(self, addr):
        GPIO.output(self.CSN, GPIO.LOW)
        time.sleep(0.001)
        self.spi_write(addr | 0x80)
        val = self.spi_read()
        time.sleep(0.001)
        GPIO.output(self.CSN, GPIO.HIGH)
        return val

    def send_strobe(self, strobe):
        GPIO.output(self.CSN, GPIO.LOW)
        time.sleep(0.001)
        self.spi_write(strobe)
        status = self.spi_read()
        time.sleep(0.001)
        GPIO.output(self.CSN, GPIO.HIGH)
        
        # Interpret status
        chip_ready = (status & 0x80) == 0
        state = status & 0x0F
        
        status_msg = "READY" if chip_ready else "NOT_READY"
        state_names = {0x00: "SLEEP", 0x01: "IDLE", 0x02: "XOFF", 0x03: "VCOON", 
                      0x04: "REGON", 0x05: "MANCAL", 0x06: "VCOON_MC", 0x07: "REGON_MC",
                      0x08: "STARTCAL", 0x09: "BWBOOST", 0x0A: "FS_LOCK", 0x0B: "IFADCON",
                      0x0C: "ENDCAL", 0x0D: "RX", 0x0E: "RX_END", 0x0F: "RX_RST",
                      0x10: "TXRX_SWITCH", 0x11: "RXFIFO_OVERFLOW", 0x12: "FSTXON",
                      0x13: "TX", 0x14: "TX_END", 0x15: "RXTX_SWITCH", 0x16: "TXFIFO_UNDERFLOW"}
        
        state_name = state_names.get(state, f"UNKNOWN_0x{state:02X}")
        print(f"[DEBUG] STROBE 0x{strobe:02X} → 0x{status:02X} ({status_msg}, {state_name})")
        
        return status

    def recover_from_error(self):
        """Recover from communication or TX errors"""
        print("[DEBUG] Attempting error recovery...")
        
        # Force reset
        GPIO.output(self.CSN, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(self.CSN, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(self.CSN, GPIO.HIGH)
        time.sleep(0.1)
        
        # Send reset strobe
        GPIO.output(self.CSN, GPIO.LOW)
        time.sleep(0.001)
        self.spi_write(0x30)  # SRES
        time.sleep(0.001)
        GPIO.output(self.CSN, GPIO.HIGH)
        time.sleep(0.2)  # Longer wait
        
        print("[DEBUG] Reset complete, reinitializing...")
        
        # Reinitialize critical registers
        self.write_register(0x0D, 0x21)  # FREQ2
        self.write_register(0x0E, 0xB0)  # FREQ1
        self.write_register(0x0F, 0x6A)  # FREQ0
        self.write_register(0x12, 0x30)  # ASK/OOK
        self.write_register(0x18, 0x16)  # MCSM0
        
        # Set power
        GPIO.output(self.CSN, GPIO.LOW)
        time.sleep(0.001)
        self.spi_write(0x7E)
        self.spi_write(0xFF)
        time.sleep(0.001)
        GPIO.output(self.CSN, GPIO.HIGH)

    def reset_and_init(self):
        """Complete reset and initialization"""
        print("[INFO] Full reset and initialization...")
        
        # Hardware reset
        GPIO.output(self.CSN, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(self.CSN, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(self.CSN, GPIO.HIGH)
        time.sleep(0.05)
        
        # Software reset
        GPIO.output(self.CSN, GPIO.LOW)
        time.sleep(0.001)
        self.spi_write(0x30)  # SRES
        time.sleep(0.001)
        GPIO.output(self.CSN, GPIO.HIGH)
        time.sleep(0.2)
        
        # Load complete configuration
        config_regs = [
            (0x0B, 0x06),  # FSCTRL1
            (0x0D, 0x21),  # FREQ2
            (0x0E, 0xB0),  # FREQ1  
            (0x0F, 0x6A),  # FREQ0
            (0x10, 0xF5),  # MDMCFG4
            (0x11, 0x83),  # MDMCFG3
            (0x12, 0x30),  # MDMCFG2 - ASK/OOK
            (0x13, 0x22),  # MDMCFG1
            (0x14, 0xF8),  # MDMCFG0
            (0x15, 0x34),  # CHANNR
            (0x18, 0x16),  # MCSM0
            (0x19, 0x1D),  # MCSM1
            (0x1C, 0xC7),  # FREND1
            (0x1D, 0x00),  # FREND0
            (0x1E, 0xB0),  # FSCAL3
            (0x21, 0xB6),  # FSCAL2
            (0x22, 0x10),  # FSCAL1
            (0x23, 0xEA),  # FSCAL0
            (0x24, 0x2A),  # FSTEST
            (0x25, 0x00),  # TEST2
            (0x26, 0x1F),  # TEST1
            (0x02, 0x06),  # IOCFG0
            (0x00, 0x29),  # IOCFG2
            (0x01, 0x2E),  # IOCFG1
            (0x08, 0x45),  # PKTCTRL0 - Fixed packet length
            (0x07, 0x04),  # PKTCTRL1
            (0x06, 0xFF),  # PKTLEN - Max packet length
        ]
        
        for addr, value in config_regs:
            self.write_register(addr, value)
            time.sleep(0.001)  # Small delay between writes
        
        # Set maximum power
        GPIO.output(self.CSN, GPIO.LOW)
        time.sleep(0.001)
        self.spi_write(0x7E)  # PATABLE
        self.spi_write(0xFF)  # Maximum power
        time.sleep(0.001)
        GPIO.output(self.CSN, GPIO.HIGH)
        
        print("[SUCCESS] ✅ Full initialization complete")

    def send_data_robust(self, data):
        """Robust data transmission with proper FIFO handling"""
        print(f"[INFO] Robust transmission of {len(data)} bytes")
        
        # Ensure we're in IDLE
        status = self.send_strobe(0x36)  # SIDLE
        if (status & 0x80) != 0:  # Chip not ready
            print("[WARN] Chip not ready, attempting recovery...")
            self.recover_from_error()
            status = self.send_strobe(0x36)
        
        time.sleep(0.01)
        
        # Flush both FIFOs
        self.send_strobe(0x3A)  # SFTX (flush TX)
        self.send_strobe(0x3B)  # SFRX (flush RX) 
        time.sleep(0.01)
        
        # Add packet length prefix to prevent underflow
        packet_data = [len(data)] + data
        print(f"[DEBUG] Sending packet: length={len(data)}, data={[hex(b) for b in data[:8]]}...")
        
        # Write packet to TX FIFO
        GPIO.output(self.CSN, GPIO.LOW)
        time.sleep(0.001)
        self.spi_write(0x3F)  # TX FIFO single write
        for byte in packet_data:
            self.spi_write(byte)
        time.sleep(0.001)
        GPIO.output(self.CSN, GPIO.HIGH)
        
        print(f"[DEBUG] Loaded {len(packet_data)} bytes into TX FIFO")
        
        # Start transmission
        tx_status = self.send_strobe(0x35)  # STX
        
        if (tx_status & 0x0F) == 0x13:  # TX state
            print("[DEBUG] ✅ Successfully entered TX state")
        else:
            print(f"[WARN] Unexpected TX status: 0x{tx_status:02X}")
        
        # Wait for transmission to complete
        print("[DEBUG] Waiting for transmission...")
        time.sleep(0.3)  # Longer wait for complete transmission
        
        # Check final status
        final_status = self.send_strobe(0x36)  # SIDLE (also gets status)
        
        return (final_status & 0x80) == 0  # Return True if chip ready

def test_robust_transmission():
    """Test the robust transmission method"""
    print("CC1101 Robust Transmission Test")
    print("=" * 40)
    
    cc = CC1101_FixedFIFO(21, 20, 19, 12, 26, 16)
    
    # Full reset and initialization
    cc.reset_and_init()
    
    # Test data - start simple
    test_patterns = [
        [0xAA, 0x55],                    # Simple alternating
        [0xFF, 0x00, 0xFF, 0x00],        # On/off pattern  
        [0xAA, 0x55, 0xAA, 0x55, 0xAA], # Longer alternating
        [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80], # Bit walking
    ]
    
    for i, pattern in enumerate(test_patterns):
        print(f"\n--- Test Pattern {i+1}/4 ---")
        print(f"[SDR] *** WATCH FOR SIGNAL - Pattern {i+1} ***")
        print(f"Data: {[hex(b) for b in pattern]}")
        
        success = cc.send_data_robust(pattern)
        
        if success:
            print("✅ Transmission successful")
        else:
            print("❌ Transmission failed, recovering...")
            cc.recover_from_error()
        
        time.sleep(3)  # Long pause between tests
    
    return cc

def send_custom_bits(cc):
    """Send your custom bit pattern with robust method"""
    print("\n" + "=" * 50)
    print("CUSTOM BIT PATTERN - ROBUST TRANSMISSION")
    print("=" * 50)
    
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
    print(f"Bytes ({len(bytes_list)}): {[hex(b) for b in bytes_list]}")
    print()
    
    # Send with robust method
    for i in range(5):
        print(f"[SDR] *** Custom Pattern Transmission {i+1}/5 ***")
        success = cc.send_data_robust(bytes_list)
        
        if not success:
            print("[WARN] Transmission failed, recovering...")
            cc.recover_from_error()
        
        time.sleep(2)
    
    print("✅ Custom pattern transmission complete!")

# Main test
if __name__ == "__main__":
    try:
        print("🔴 PREPARE SDR FOR 433.92 MHz")
        print("Looking for improved transmission signals...")
        print()
        
        working_cc = test_robust_transmission()
        
        if working_cc:
            input("\nDid you see any signals? Press ENTER to send custom pattern...")
            send_custom_bits(working_cc)
        
    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        GPIO.cleanup()
        print("GPIO cleanup complete")

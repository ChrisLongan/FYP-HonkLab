import RPi.GPIO as GPIO
import time

def ultra_slow_spi_test():
    """Test CC1101 with extremely slow SPI to isolate timing issues"""
    
    print("CC1101 Ultra-Slow SPI Test")
    print("=" * 40)
    
    # Pin setup
    SCK = 21
    MOSI = 20
    MISO = 19
    CSN = 12
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(SCK, GPIO.OUT)
    GPIO.setup(MOSI, GPIO.OUT)
    GPIO.setup(MISO, GPIO.IN)
    GPIO.setup(CSN, GPIO.OUT)
    
    GPIO.output(SCK, GPIO.LOW)
    GPIO.output(MOSI, GPIO.LOW)
    GPIO.output(CSN, GPIO.HIGH)
    
    print("Pin setup complete")
    
    def ultra_slow_reset():
        """Super slow reset sequence"""
        print("\n1. Ultra-slow reset sequence...")
        
        # Power-on reset
        GPIO.output(CSN, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(CSN, GPIO.LOW)
        time.sleep(0.1)
        GPIO.output(CSN, GPIO.HIGH)
        time.sleep(0.1)
        
        # Send SRES command extremely slowly
        GPIO.output(CSN, GPIO.LOW)
        time.sleep(0.01)
        
        # Send 0x30 (SRES) bit by bit with 10ms delays
        sres_cmd = 0x30
        print("   Sending SRES command 0x30...")
        
        for bit in range(8):
            bit_val = (sres_cmd & (1 << (7 - bit))) != 0
            
            GPIO.output(SCK, GPIO.LOW)
            time.sleep(0.01)  # 10ms delay
            GPIO.output(MOSI, bit_val)
            time.sleep(0.01)
            print(f"     Bit {bit}: {int(bit_val)}")
            GPIO.output(SCK, GPIO.HIGH)
            time.sleep(0.01)
        
        GPIO.output(SCK, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(CSN, GPIO.HIGH)
        time.sleep(0.2)  # Long wait after reset
        
        print("   Reset command sent")
    
    def ultra_slow_version_read():
        """Read VERSION register with extreme delays"""
        print("\n2. Ultra-slow VERSION register read...")
        
        GPIO.output(CSN, GPIO.LOW)
        time.sleep(0.01)
        
        # Send 0xB1 (0x31 | 0x80 = VERSION register read)
        version_cmd = 0xB1
        print(f"   Sending VERSION read command 0x{version_cmd:02X}...")
        
        # Send command
        for bit in range(8):
            bit_val = (version_cmd & (1 << (7 - bit))) != 0
            
            GPIO.output(SCK, GPIO.LOW)
            time.sleep(0.01)
            GPIO.output(MOSI, bit_val)
            time.sleep(0.01)
            GPIO.output(SCK, GPIO.HIGH)
            time.sleep(0.01)
        
        GPIO.output(SCK, GPIO.LOW)
        time.sleep(0.01)
        
        # Read response
        print("   Reading response...")
        version = 0
        response_bits = []
        
        for bit in range(8):
            GPIO.output(SCK, GPIO.HIGH)
            time.sleep(0.01)
            bit_val = GPIO.input(MISO)
            response_bits.append(bit_val)
            if bit_val:
                version |= (1 << (7 - bit))
            time.sleep(0.01)
            GPIO.output(SCK, GPIO.LOW)
            time.sleep(0.01)
        
        GPIO.output(CSN, GPIO.HIGH)
        
        print(f"   Response bits: {response_bits}")
        print(f"   VERSION result: 0x{version:02X}")
        
        return version
    
    def check_pin_states():
        """Check all pin states"""
        print("\n3. Checking pin states...")
        print(f"   SCK:  {GPIO.input(SCK)}")
        print(f"   MOSI: {GPIO.input(MOSI)}")  
        print(f"   MISO: {GPIO.input(MISO)}")
        print(f"   CSN:  {GPIO.input(CSN)}")
    
    def test_miso_during_transaction():
        """Monitor MISO throughout a transaction"""
        print("\n4. MISO monitoring test...")
        
        print("   MISO before transaction:", GPIO.input(MISO))
        
        GPIO.output(CSN, GPIO.LOW)
        print("   MISO after CSN LOW:", GPIO.input(MISO))
        time.sleep(0.01)
        
        # Send a few clock pulses and monitor MISO
        for i in range(8):
            GPIO.output(SCK, GPIO.HIGH)
            time.sleep(0.01)
            miso_high = GPIO.input(MISO)
            GPIO.output(SCK, GPIO.LOW)
            time.sleep(0.01)
            miso_low = GPIO.input(MISO)
            print(f"   Clock {i}: MISO = {miso_high} (SCK high), {miso_low} (SCK low)")
        
        GPIO.output(CSN, GPIO.HIGH)
        print("   MISO after CSN HIGH:", GPIO.input(MISO))
    
    # Run tests
    try:
        check_pin_states()
        ultra_slow_reset()
        version1 = ultra_slow_version_read()
        
        if version1 != 0x14:
            print(f"\n❌ First attempt failed: 0x{version1:02X}")
            print("Trying again with even longer delays...")
            
            time.sleep(0.5)
            ultra_slow_reset()
            time.sleep(0.5)
            version2 = ultra_slow_version_read()
            
            if version2 != 0x14:
                print(f"❌ Second attempt also failed: 0x{version2:02X}")
                test_miso_during_transaction()
                
                print("\n" + "=" * 40)
                print("HARDWARE DIAGNOSIS")
                print("=" * 40)
                print("Since the manual slow test from earlier worked,")
                print("but this automated version doesn't, possible issues:")
                print()
                print("1. 🔄 Timing still too fast (try 100ms delays)")
                print("2. 🔌 Loose connection - try wiggling wires")
                print("3. ⚡ Power fluctuation - check power supply")
                print("4. 📱 GPIO conflict with LCD - try different pins")
                print("5. 🧠 Pi overloaded - close other programs")
                
            else:
                print(f"✅ SUCCESS on second attempt: 0x{version2:02X}")
        else:
            print(f"✅ SUCCESS on first attempt: 0x{version1:02X}")
            
    except Exception as e:
        print(f"Error during test: {e}")
    finally:
        GPIO.cleanup()

def try_different_approach():
    """Try the exact approach that worked in the manual test"""
    print("\n" + "=" * 40)
    print("RECREATING WORKING MANUAL TEST")
    print("=" * 40)
    
    SCK = 21
    MOSI = 20  
    MISO = 19
    CSN = 12
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(SCK, GPIO.OUT)
    GPIO.setup(MOSI, GPIO.OUT)
    GPIO.setup(MISO, GPIO.IN)
    GPIO.setup(CSN, GPIO.OUT)
    
    GPIO.output(SCK, GPIO.LOW)
    GPIO.output(MOSI, GPIO.LOW)
    GPIO.output(CSN, GPIO.HIGH)
    
    try:
        # Exact sequence from working manual test
        print("Recreating the exact sequence that gave 0x14...")
        
        # Enhanced reset (from manual test)
        GPIO.output(CSN, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(CSN, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(CSN, GPIO.HIGH)
        time.sleep(0.05)
        
        GPIO.output(CSN, GPIO.LOW)
        
        # Send 0x30 (SRES) - using exact same method as working test
        for bit in range(8):
            GPIO.output(SCK, GPIO.LOW)
            time.sleep(0.001)
            GPIO.output(MOSI, (0x30 & (1 << (7 - bit))) != 0)
            time.sleep(0.001)
            GPIO.output(SCK, GPIO.HIGH)
            time.sleep(0.001)
        GPIO.output(SCK, GPIO.LOW)
        
        GPIO.output(CSN, GPIO.HIGH)
        time.sleep(0.1)
        
        # Now try VERSION read with exact same timing
        GPIO.output(CSN, GPIO.LOW)
        time.sleep(0.001)
        
        # Send 0xF1 (VERSION with burst bit, like in working test)
        command = 0xF1
        for bit in range(8):
            GPIO.output(SCK, GPIO.LOW)
            time.sleep(0.001)
            GPIO.output(MOSI, (command & (1 << (7 - bit))) != 0)
            time.sleep(0.001)
            GPIO.output(SCK, GPIO.HIGH)
            time.sleep(0.001)
        
        GPIO.output(SCK, GPIO.LOW)
        time.sleep(0.001)
        
        # Read response exactly like working test
        version = 0
        for bit in range(8):
            GPIO.output(SCK, GPIO.HIGH)
            time.sleep(0.001)
            bit_val = GPIO.input(MISO)
            if bit_val:
                version |= (1 << (7 - bit))
            GPIO.output(SCK, GPIO.LOW)
            time.sleep(0.001)
        
        GPIO.output(CSN, GPIO.HIGH)
        
        print(f"Recreated test result: 0x{version:02X}")
        
        if version == 0x14:
            print("✅ SUCCESS! The exact timing from manual test works!")
            return True
        else:
            print("❌ Manual test recreation failed")
            return False
            
    except Exception as e:
        print(f"Error recreating manual test: {e}")
        return False
    finally:
        GPIO.cleanup()

# Run both tests
if __name__ == "__main__":
    # First try ultra slow
    ultra_slow_spi_test()
    
    time.sleep(2)
    
    # Then try recreating the exact working test
    try_different_approach()

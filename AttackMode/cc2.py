#test
from cc1101_softspi import CC1101
import RPi.GPIO as GPIO
import time

def test_spi_communication(cc):
    """Test basic SPI communication with CC1101"""
    print("=" * 60)
    print("CC1101 SPI COMMUNICATION TEST")
    print("=" * 60)
    
    # Test 1: Check VERSION register multiple times
    print("\n1. Testing VERSION register (should be 0x14):")
    for i in range(5):
        version = cc.read_register(0x31)
        print(f"   Attempt {i+1}: VERSION = 0x{version:02X}")
        time.sleep(0.1)
    
    # Test 2: Test write/read to a writable register
    print("\n2. Testing write/read to FSCTRL1 register (0x07):")
    original = cc.read_register(0x07)
    print(f"   Original value: 0x{original:02X}")
    
    # Write test values and read back
    test_values = [0xAA, 0x55, 0x00, 0xFF]
    for test_val in test_values:
        cc.write_register(0x07, test_val)
        readback = cc.read_register(0x07)
        status = "✓ PASS" if readback == test_val else "✗ FAIL"
        print(f"   Write 0x{test_val:02X} → Read 0x{readback:02X} {status}")
    
    # Restore original value
    cc.write_register(0x07, original)
    
    # Test 3: Test strobe commands
    print("\n3. Testing strobe commands:")
    strobes = [0x30, 0x36, 0x34]  # SRES, SIDLE, SRX
    for strobe in strobes:
        status = cc.send_strobe(strobe)
        print(f"   Strobe 0x{strobe:02X} → Status: 0x{status:02X}")
    
    # Test 4: Check pin states
    print("\n4. GPIO Pin States:")
    print(f"   CSN:  {GPIO.input(cc.CSN)}")
    print(f"   GDO0: {GPIO.input(cc.GDO0)}")
    print(f"   GDO2: {GPIO.input(cc.GDO2)}")
    print(f"   MISO: {GPIO.input(cc.MISO)}")

def test_pin_wiring(cc):
    """Test individual pin connections"""
    print("\n" + "=" * 60)
    print("PIN WIRING TEST")
    print("=" * 60)
    
    print("\nTesting CSN (Chip Select) control:")
    for i in range(3):
        GPIO.output(cc.CSN, GPIO.HIGH)
        time.sleep(0.1)
        print(f"   CSN HIGH: {GPIO.input(cc.CSN)}")
        
        GPIO.output(cc.CSN, GPIO.LOW)
        time.sleep(0.1)
        print(f"   CSN LOW:  {GPIO.input(cc.CSN)}")
    
    GPIO.output(cc.CSN, GPIO.HIGH)  # Return to idle state

def enhanced_reset_sequence(cc):
    """Try enhanced reset sequence"""
    print("\n" + "=" * 60)
    print("ENHANCED RESET SEQUENCE")
    print("=" * 60)
    
    print("1. Power-on reset sequence...")
    
    # Ensure CSN is high
    GPIO.output(cc.CSN, GPIO.HIGH)
    time.sleep(0.1)
    
    # Toggle CSN for power-on reset
    GPIO.output(cc.CSN, GPIO.LOW)
    time.sleep(0.01)
    GPIO.output(cc.CSN, GPIO.HIGH)
    time.sleep(0.05)  # Wait for chip to be ready
    
    print("2. Sending SRES strobe...")
    GPIO.output(cc.CSN, GPIO.LOW)
    cc.spi_write(0x30)  # SRES
    GPIO.output(cc.CSN, GPIO.HIGH)
    time.sleep(0.1)
    
    print("3. Checking if reset worked...")
    version = cc.read_register(0x31)
    print(f"   VERSION after reset: 0x{version:02X}")
    
    return version == 0x14

def slow_spi_test(cc):
    """Test with slower SPI timing"""
    print("\n" + "=" * 60)
    print("SLOW SPI TEST")
    print("=" * 60)
    
    # Temporarily modify SPI timing
    original_spi_write = cc.spi_write
    original_spi_read = cc.spi_read
    
    def slow_spi_write(byte):
        for i in range(8):
            GPIO.output(cc.SCK, GPIO.LOW)
            time.sleep(0.00001)  # 10μs delay
            GPIO.output(cc.MOSI, (byte & (1 << (7 - i))) != 0)
            time.sleep(0.00001)
            GPIO.output(cc.SCK, GPIO.HIGH)
            time.sleep(0.00001)
        GPIO.output(cc.SCK, GPIO.LOW)
    
    def slow_spi_read():
        value = 0
        for i in range(8):
            GPIO.output(cc.SCK, GPIO.HIGH)
            time.sleep(0.00001)
            if GPIO.input(cc.MISO):
                value |= (1 << (7 - i))
            time.sleep(0.00001)
            GPIO.output(cc.SCK, GPIO.LOW)
            time.sleep(0.00001)
        return value
    
    # Replace with slow versions
    cc.spi_write = slow_spi_write
    cc.spi_read = slow_spi_read
    
    print("Testing with 10μs SPI delays...")
    version = cc.read_register(0x31)
    print(f"VERSION with slow SPI: 0x{version:02X}")
    
    # Restore original functions
    cc.spi_write = original_spi_write
    cc.spi_read = original_spi_read
    
    return version == 0x14

# === Main Debug Program ===
print("CC1101 Hardware Debug Tool")
print("Checking your pin assignments:")
print("  SCK:  GPIO 21")
print("  MOSI: GPIO 20") 
print("  MISO: GPIO 19")
print("  CSN:  GPIO 12")
print("  GDO0: GPIO 26")
print("  GDO2: GPIO 16")

cc = CC1101(
    sck=21,
    mosi=20, 
    miso=19,
    csn=12,
    gdo0=26,
    gdo2=16
)

try:
    # Initial state
    print(f"\nInitial CSN state: {GPIO.input(cc.CSN)}")
    print(f"Initial MISO state: {GPIO.input(cc.MISO)}")
    
    # Test basic communication
    test_spi_communication(cc)
    
    # Test pin wiring
    test_pin_wiring(cc)
    
    # Try enhanced reset
    reset_success = enhanced_reset_sequence(cc)
    
    if not reset_success:
        print("\nStandard reset failed, trying slow SPI...")
        slow_success = slow_spi_test(cc)
        
        if slow_success:
            print("✓ SUCCESS: Slow SPI timing works!")
            print("Your CC1101 needs slower SPI timing.")
        else:
            print("✗ FAILED: Even slow SPI doesn't work.")
            print("\nPOSSIBLE ISSUES:")
            print("1. Wiring problem (check connections)")
            print("2. Power supply (CC1101 needs 3.3V)")
            print("3. Bad CC1101 module")
            print("4. GPIO pin conflicts")
    else:
        print("✓ SUCCESS: CC1101 communication working!")

except Exception as e:
    print(f"\nError during testing: {e}")
finally:
    GPIO.cleanup()
    print("\nGPIO cleanup complete")

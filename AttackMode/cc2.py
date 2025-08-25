from cc1101_softspi import CC1101
import RPi.GPIO as GPIO
import time

def safe_miso_test():
    """Safe test that won't crash the Pi"""
    print("CC1101 Safe MISO Test")
    print("=" * 40)
    
    # Only initialize the pins we're already using
    cc = CC1101(21, 20, 19, 12, 26, 16)
    
    print("Current pin assignments:")
    print("  SCK:  GPIO 21")
    print("  MOSI: GPIO 20") 
    print("  MISO: GPIO 19 ← Problem pin")
    print("  CSN:  GPIO 12")
    print()
    
    # Test 1: Check initial MISO state
    print("1. Checking MISO pin state...")
    for i in range(5):
        miso_state = GPIO.input(19)
        print(f"   MISO reading {i+1}: {miso_state}")
        time.sleep(0.2)
    
    # Test 2: Try to communicate
    print("\n2. Testing communication...")
    cc.reset()
    time.sleep(0.1)
    
    version = cc.read_register(0x31)
    print(f"   VERSION register: 0x{version:02X} (should be 0x14)")
    
    # Test 3: Manual bit check
    print("\n3. Manual SPI test...")
    GPIO.output(cc.CSN, GPIO.LOW)
    
    # Send VERSION register read command (0x31 | 0x80 = 0xB1)
    cc.spi_write(0xB1)
    
    # Read the response bit by bit
    print("   Reading response bits:")
    value = 0
    for bit in range(8):
        GPIO.output(cc.SCK, GPIO.HIGH)
        time.sleep(0.00001)
        bit_val = GPIO.input(cc.MISO)
        GPIO.output(cc.SCK, GPIO.LOW)
        time.sleep(0.00001)
        
        if bit_val:
            value |= (1 << (7 - bit))
            
        print(f"     Bit {bit}: {bit_val}")
    
    GPIO.output(cc.CSN, GPIO.HIGH)
    print(f"   Reconstructed byte: 0x{value:02X}")
    
    return version == 0x14

def simple_wire_test():
    """Test if MISO wire is connected at all"""
    print("\n" + "=" * 40)
    print("SIMPLE WIRE CONNECTION TEST")
    print("=" * 40)
    print("This will help determine if MISO is physically connected.")
    print()
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Set pull-down
    time.sleep(0.1)
    
    miso_with_pulldown = GPIO.input(19)
    print(f"MISO with pull-down resistor: {miso_with_pulldown}")
    
    GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Set pull-up
    time.sleep(0.1)
    
    miso_with_pullup = GPIO.input(19)
    print(f"MISO with pull-up resistor:   {miso_with_pullup}")
    
    GPIO.setup(19, GPIO.IN)  # Back to normal input
    
    if miso_with_pulldown == 0 and miso_with_pullup == 1:
        print("✓ MISO pin responds to pull resistors - GPIO is working")
        print("✗ But CC1101 might not be connected or powered")
    elif miso_with_pulldown == 1 and miso_with_pullup == 1:
        print("✗ MISO stuck HIGH - either:")
        print("  1. CC1101 is driving it high (good)")
        print("  2. Short to 3.3V somewhere (bad)")
    elif miso_with_pulldown == 0 and miso_with_pullup == 0:
        print("✗ MISO stuck LOW - probably shorted to ground")
    else:
        print("? Unexpected result - hardware issue likely")

# Run safe tests only
try:
    # Test current setup
    success = safe_miso_test()
    
    if not success:
        simple_wire_test()
        
        print("\n" + "=" * 40)
        print("RECOMMENDED ACTIONS:")
        print("=" * 40)
        print("1. Check physical MISO wire connection")
        print("2. Verify CC1101 power (3.3V to VCC)")
        print("3. Try different MISO wire")
        print("4. If possible, swap to different GPIO pin")
        print("\nSAFE pins to try for MISO: 18, 23, 24, 25")
        print("(Avoid pins used by your LCD)")

except Exception as e:
    print(f"Error: {e}")
    print("Even the safe test failed - serious hardware issue")

fina

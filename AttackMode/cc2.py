from cc1101_softspi import CC1101
import RPi.GPIO as GPIO
import time

def test_power_and_signals():
    """Test CC1101 power and control signals"""
    print("CC1101 Power and Signal Test")
    print("=" * 40)
    
    cc = CC1101(21, 20, 19, 12, 26, 16)
    
    print("Testing control signals...")
    print()
    
    # Test 1: CSN Control
    print("1. Testing CSN (Chip Select) control:")
    for i in range(3):
        GPIO.output(cc.CSN, GPIO.HIGH)
        csn_high = GPIO.input(cc.CSN)
        time.sleep(0.1)
        
        GPIO.output(cc.CSN, GPIO.LOW) 
        csn_low = GPIO.input(cc.CSN)
        time.sleep(0.1)
        
        print(f"   Test {i+1}: CSN HIGH={csn_high}, LOW={csn_low}")
    
    # Test 2: Check GDO pins (these should respond if CC1101 has power)
    print("\n2. Testing GDO pins (should change if CC1101 powered):")
    
    # Reset sequence - GDO pins should change if CC1101 is alive
    GPIO.output(cc.CSN, GPIO.HIGH)
    time.sleep(0.1)
    gdo0_before = GPIO.input(cc.GDO0)
    gdo2_before = GPIO.input(cc.GDO2)
    
    print(f"   Before reset: GDO0={gdo0_before}, GDO2={gdo2_before}")
    
    # Try reset
    cc.reset()
    time.sleep(0.2)
    
    gdo0_after = GPIO.input(cc.GDO0)
    gdo2_after = GPIO.input(cc.GDO2)
    
    print(f"   After reset:  GDO0={gdo0_after}, GDO2={gdo2_after}")
    
    if gdo0_before != gdo0_after or gdo2_before != gdo2_after:
        print("   ✓ GDO pins changed - CC1101 might be powered!")
    else:
        print("   ✗ GDO pins didn't change - power issue likely")
    
    # Test 3: Extended reset sequence
    print("\n3. Testing extended power-on reset:")
    
    # Power cycle simulation
    GPIO.output(cc.CSN, GPIO.LOW)
    time.sleep(0.01)
    GPIO.output(cc.CSN, GPIO.HIGH) 
    time.sleep(0.1)  # Wait longer for power stabilization
    
    # Check if MISO goes low briefly (sign of CC1101 reset)
    print("   Monitoring MISO during reset...")
    
    GPIO.output(cc.CSN, GPIO.LOW)
    cc.spi_write(0x30)  # SRES command
    
    # Monitor MISO for changes during command
    miso_states = []
    for i in range(10):
        miso_states.append(GPIO.input(cc.MISO))
        time.sleep(0.001)
    
    GPIO.output(cc.CSN, GPIO.HIGH)
    time.sleep(0.1)
    
    print(f"   MISO states during reset: {miso_states}")
    
    if any(state == 0 for state in miso_states):
        print("   ✓ MISO went low - CC1101 responded!")
    else:
        print("   ✗ MISO stayed high - CC1101 not responding")
    
    # Test 4: Try reading VERSION with very slow timing
    print("\n4. Testing with very slow SPI timing:")
    
    # Manual super-slow SPI read
    GPIO.output(cc.CSN, GPIO.LOW)
    time.sleep(0.001)  # 1ms delay
    
    # Send 0xF1 (VERSION register read with burst bit)
    command = 0xF1
    for bit in range(8):
        GPIO.output(cc.SCK, GPIO.LOW)
        time.sleep(0.001)
        GPIO.output(cc.MOSI, (command & (1 << (7 - bit))) != 0)
        time.sleep(0.001)
        GPIO.output(cc.SCK, GPIO.HIGH)
        time.sleep(0.001)
    
    GPIO.output(cc.SCK, GPIO.LOW)
    time.sleep(0.001)
    
    # Read response very slowly
    version = 0
    print("   Slow read bits: ", end="")
    for bit in range(8):
        GPIO.output(cc.SCK, GPIO.HIGH)
        time.sleep(0.001)
        bit_val = GPIO.input(cc.MISO)
        print(bit_val, end="")
        if bit_val:
            version |= (1 << (7 - bit))
        GPIO.output(cc.SCK, GPIO.LOW)
        time.sleep(0.001)
    
    GPIO.output(cc.CSN, GPIO.HIGH)
    print(f"\n   Slow VERSION result: 0x{version:02X}")
    
    return version

def power_diagnosis():
    """Provide power diagnosis based on test results"""
    print("\n" + "=" * 40)
    print("DIAGNOSIS AND NEXT STEPS")
    print("=" * 40)
    
    print("\nSince MISO responds to pull-up/down but reads 0 in communication:")
    print()
    print("Most likely issues (in order):")
    print("1. 🔋 POWER: CC1101 not getting stable 3.3V")
    print("2. 🔌 GROUND: Missing or loose ground connection") 
    print("3. 📶 CSN: Chip Select not working properly")
    print("4. ⚡ MOSI: Data line to CC1101 broken")
    print("5. 🕐 TIMING: SPI timing too fast")
    print()
    print("IMMEDIATE ACTIONS TO TRY:")
    print("📋 1. Check CC1101 power LED (if it has one)")
    print("📋 2. Verify VCC wire goes to 3.3V (NOT 5V)")
    print("📋 3. Check ground wire connection")
    print("📋 4. Try different jumper wires")
    print("📋 5. Measure voltage with multimeter if available")

# Run the test
try:
    version = test_power_and_signals()
    
    if version == 0x14:
        print("\n🎉 SUCCESS! CC1101 is now responding!")
        print("The slow timing worked - your SPI was too fast.")
    elif version != 0x00:
        print(f"\n⚠️  Got response 0x{version:02X} but not expected 0x14")
        print("CC1101 is powered but may have issues.")
    else:
        power_diagnosis()

except Exception as e:
    print(f"\nError during test: {e}")
    power_diagnosis()

finally:
    GPIO.cleanup()

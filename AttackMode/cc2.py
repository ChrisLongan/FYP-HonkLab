#test
from cc1101_softspi import CC1101
import RPi.GPIO as GPIO
import time

def test_different_miso_pins():
    """Test CC1101 with different MISO pins to isolate the problem"""
    
    # Alternative GPIO pins to try for MISO
    alternative_pins = [18, 23, 24, 25, 8, 7, 1, 13]
    
    print("Testing CC1101 with different MISO pins...")
    print("Current assignment: MISO = GPIO 19 (not working)")
    print()
    
    for alt_pin in alternative_pins:
        print(f"=== Testing MISO on GPIO {alt_pin} ===")
        
        try:
            # Initialize CC1101 with alternative MISO pin
            cc = CC1101(
                sck=21,
                mosi=20,
                miso=alt_pin,  # Try different pin
                csn=12,
                gdo0=26,
                gdo2=16
            )
            
            # Check initial MISO state
            miso_state = GPIO.input(alt_pin)
            print(f"Initial MISO state on GPIO {alt_pin}: {miso_state}")
            
            # Try to read VERSION register
            cc.reset()
            time.sleep(0.1)
            
            for attempt in range(3):
                version = cc.read_register(0x31)
                print(f"  Attempt {attempt+1}: VERSION = 0x{version:02X}")
                
                if version == 0x14:
                    print(f"🎉 SUCCESS! CC1101 responds on GPIO {alt_pin}")
                    print(f"Change your MISO pin from GPIO 19 to GPIO {alt_pin}")
                    return alt_pin
                    
            print(f"❌ Failed on GPIO {alt_pin}")
            
        except Exception as e:
            print(f"❌ Error testing GPIO {alt_pin}: {e}")
        
        print()
        
        # Clean up
        GPIO.cleanup()
        time.sleep(0.5)
    
    print("❌ No working MISO pin found - hardware problem likely")
    return None

def quick_hardware_test():
    """Quick test of current wiring"""
    print("=== QUICK HARDWARE TEST ===")
    
    cc = CC1101(21, 20, 19, 12, 26, 16)
    
    # Test if MISO changes when we toggle other pins
    print("Testing if MISO responds to activity...")
    
    for i in range(5):
        # Toggle CSN and check if MISO changes
        GPIO.output(cc.CSN, GPIO.LOW)
        time.sleep(0.01)
        miso1 = GPIO.input(cc.MISO)
        
        GPIO.output(cc.CSN, GPIO.HIGH)  
        time.sleep(0.01)
        miso2 = GPIO.input(cc.MISO)
        
        print(f"  CSN Low→High: MISO {miso1}→{miso2}")
        
        if miso1 != miso2:
            print("✓ MISO is responding - wiring might be OK")
            break
    else:
        print("❌ MISO stuck - wiring problem")

# Run the tests
print("CC1101 MISO PIN DIAGNOSTIC")
print("=" * 50)

# First, quick test current wiring
quick_hardware_test()
print()

# Then try alternative pins
working_pin = test_different_miso_pins()

if working_pin:
    print("=" * 50)
    print("SOLUTION FOUND!")
    print(f"Update your code to use GPIO {working_pin} for MISO instead of GPIO 19")
    print()
    print("Change this line in your code:")
    print("  OLD: miso=19")
    print(f"  NEW: miso={working_pin}")
else:
    print("=" * 50)
    print("HARDWARE ISSUE DETECTED")
    print("Possible solutions:")
    print("1. Check/replace MISO wire connection")
    print("2. Try a different CC1101 module")
    print("3. Verify CC1101 power supply (3.3V)")

GPIO.cleanup()

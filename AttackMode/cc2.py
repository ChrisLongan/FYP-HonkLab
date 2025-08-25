#test
from cc1101_softspi import CC1101
import RPi.GPIO as GPIO
import time

def send_ook_bits_raw(cc1101, bit_string, bit_duration_us=500):
    """
    Send OOK bits by manually controlling the CC1101 carrier
    This bypasses packet mode and directly controls TX on/off
    """
    print(f"Sending {len(bit_string)} bits with {bit_duration_us}μs per bit")
    print(f"Bit pattern: {bit_string}")
    
    # Configure for continuous TX mode
    cc1101.write_register(0x08, 0x12)  # PKTCTRL0 - disable packet mode
    cc1101.write_register(0x12, 0x30)  # MDMCFG2 - ASK/OOK, no sync
    cc1101.write_register(0x02, 0x2F)  # IOCFG0 - high impedance when idle
    
    # Start continuous TX
    cc1101.send_strobe(0x35)  # STX
    time.sleep(0.01)
    
    # Check if we entered TX mode
    state = cc1101.get_marc_state()
    if state != 0x13:  # TX state
        print(f"[ERROR] Failed to enter TX mode, MARCSTATE: 0x{state:02X}")
        return False
    
    print("[INFO] Entered continuous TX mode, sending bits...")
    
    # Send each bit by controlling TX enable
    for i, bit in enumerate(bit_string):
        if bit == '1':
            # Turn ON carrier
            cc1101.send_strobe(0x35)  # STX (turn on TX)
        else:
            # Turn OFF carrier  
            cc1101.send_strobe(0x36)  # SIDLE (turn off TX)
            
        # Wait for bit duration
        time.sleep(bit_duration_us / 1000000.0)
        
        # Debug every 10 bits
        if (i + 1) % 10 == 0:
            print(f"[DEBUG] Sent {i + 1} bits...")
    
    # Return to idle
    cc1101.send_strobe(0x36)  # SIDLE
    print("[INFO] Transmission complete, returned to idle")
    return True

def send_traditional_pattern(cc1101, bit_string, repeat=3, inter_frame_delay_ms=10):
    """
    Send bit pattern using traditional OOK timing
    """
    for rep in range(repeat):
        print(f"\n=== Transmission {rep + 1} of {repeat} ===")
        success = send_ook_bits_raw(cc1101, bit_string, bit_duration_us=400)
        
        if not success:
            print(f"[ERROR] Transmission {rep + 1} failed!")
            return False
            
        if rep < repeat - 1:
            time.sleep(inter_frame_delay_ms / 1000.0)
    
    return True

# === Initialize CC1101 ===
print("Initializing CC1101 for raw OOK transmission...")
cc = CC1101(
    sck=21,
    mosi=20,
    miso=19,
    csn=12,
    gdo0=26,
    gdo2=16
)

# === Basic setup ===
cc.reset()
time.sleep(0.2)

# Check communication
print("Testing SPI communication...")
version = cc.read_register(0x31)  # VERSION register
print(f"CC1101 VERSION: 0x{version:02X} (should be 0x14)")

if version != 0x14:
    print("[ERROR] CC1101 not responding correctly! Check wiring.")
    exit(1)

# Basic initialization
cc.init()
cc.set_frequency(433.92)
cc.set_power_level(7)  # Max power

print("CC1101 ready for raw OOK transmission!")
print("=" * 60)

# === Your bit pattern ===
your_bits = "1000111010001110100010001000111011101110111011101110111010001110100011101110111010001000100011101"

try:
    # Send using raw bit method
    success = send_traditional_pattern(cc, your_bits, repeat=5, inter_frame_delay_ms=20)
    
    if success:
        print("\n" + "=" * 60)
        print("All transmissions completed successfully!")
    else:
        print("\n[ERROR] Some transmissions failed!")

except KeyboardInterrupt:
    print("\nTransmission interrupted by user")
except Exception as e:
    print(f"\nError: {e}")
finally:
    # Make sure we're in idle state
    cc.send_strobe(0x36)  # SIDLE
    GPIO.cleanup()
    print("GPIO cleanup complete")

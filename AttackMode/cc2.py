#test
from cc1101_softspi import CC1101
import RPi.GPIO as GPIO
import time

def binary_string_to_bytes(binary_str):
    """
    Convert binary string to list of bytes for CC1101 transmission
    Pads with leading zeros if needed to make complete bytes
    """
    # Remove any spaces or newlines
    binary_str = binary_str.replace(' ', '').replace('\n', '')
    
    # Pad to make it divisible by 8 bits
    while len(binary_str) % 8 != 0:
        binary_str = '0' + binary_str
    
    # Convert to bytes
    bytes_list = []
    for i in range(0, len(binary_str), 8):
        byte_chunk = binary_str[i:i+8]
        byte_value = int(byte_chunk, 2)
        bytes_list.append(byte_value)
    
    return bytes_list, binary_str

def send_key_fob_pattern(cc1101, bit_pattern, repeat_count=5, delay_ms=10):
    """
    Send key fob bit pattern with typical repetition
    """
    payload, padded_bits = binary_string_to_bytes(bit_pattern)
    
    print(f"Original bits: {bit_pattern}")
    print(f"Padded bits:   {padded_bits}")
    print(f"Length: {len(bit_pattern)} bits → {len(payload)} bytes")
    print(f"Payload bytes: {[hex(b) for b in payload]}")
    print(f"Payload bytes: {payload}")
    print("-" * 60)
    
    for transmission in range(repeat_count):
        print(f"[TX {transmission + 1}/{repeat_count}] Sending pattern...")
        cc1101.send_data(payload)
        
        # Check GDO0 state after transmission
        gdo0_state = GPIO.input(cc1101.GDO0)
        print(f"[DEBUG] GDO0 state: {gdo0_state}")
        
        if transmission < repeat_count - 1:  # Don't delay after last transmission
            time.sleep(delay_ms / 1000.0)
    
    print(f"\nCompleted {repeat_count} transmissions!")

# === Initialize CC1101 ===
print("Initializing CC1101...")
cc = CC1101(
    sck=21,
    mosi=20,
    miso=19,
    csn=12,
    gdo0=26,
    gdo2=16
)

# === Configure the radio ===
print("Configuring radio...")
cc.reset()
time.sleep(0.1)
cc.init()
cc.set_frequency(433.92)         # 433.92 MHz
cc.set_modulation('ASK_OOK')     # On-Off Keying for key fobs
cc.set_power_level(0)            # Maximum power

print("Radio ready!")
print("=" * 60)

# === Your specific bit pattern ===
your_bits = "1000111010001110100010001000111011101110111011101110111010001110100011101110111010001000100011101"

try:
    # Send the pattern
    send_key_fob_pattern(cc, your_bits, repeat_count=3, delay_ms=10)
    
    print("\nWaiting 3 seconds...")
    time.sleep(3)
    
    # Send again (simulating button press)
    print("\nSending second burst...")
    send_key_fob_pattern(cc, your_bits, repeat_count=3, delay_ms=10)

except KeyboardInterrupt:
    print("\nTransmission stopped by user")
except Exception as e:
    print(f"\nError: {e}")
finally:
    # Clean up GPIO
    GPIO.cleanup()
    print("GPIO cleanup complete")

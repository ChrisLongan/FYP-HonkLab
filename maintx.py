from softspi import CC1101
import RPi.GPIO as GPIO
import time

# === Initialize CC1101 on software SPI pins ===
cc = CC1101(
    sck=21,
    mosi=20,
    miso=19,
    csn=12,       # You said you're using GPIO 12 for CSN
    gdo0=26,      # GDO0 pin (used to confirm TX activity)
    gdo2=16       # Optional
)

# === Reset and initialize CC1101 ===
cc.reset()
cc.init()

# === Configure TX parameters ===
cc.set_frequency(433.92)         # Frequency in MHz
cc.set_modulation('ASK_OOK')     # Or '2-FSK'
cc.set_power_level(0)            # Max TX power (0 = strongest)

# === Define payload ===
payload = [0xAA] * 32            # Alternating bit pattern (visible on SDR)

# === Transmission loop ===
print("[INFO] Starting transmission loop...\n")
for i in range(10):
    print(f"[{i+1}] Sending payload...")
    cc.send_data(payload)
    
    # Read and print GDO0 immediately after TX
    gdo0_state = GPIO.input(26)
    print(f"[DEBUG] GDO0 state after TX: {gdo0_state}\n")
    
    time.sleep(1)

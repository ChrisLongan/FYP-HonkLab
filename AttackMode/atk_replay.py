
import time
from cc1101_softspi import CC1101
import RPi.GPIO as GPIO
import os

def read_latest_payload(decoder_type="keeloq"):
    path = f"latest_{decoder_type.lower()}.txt"
    if not os.path.exists(path):
        print(f"[ERROR] No latest decode file found: {path}")
        return None
    with open(path, "r") as f:
        hex_data = f.read().strip()
        return [int(hex_data[i:i+2], 16) for i in range(0, len(hex_data), 2)]

def main():
    decoder_type = "keeloq"  # change to "fsk" or "ook" if needed
    sck, mosi, miso, csn, gdo0, gdo2 = 21, 20, 19, 18, 26, 16

    payload = read_latest_payload(decoder_type)
    if payload is None:
        return

    cc = CC1101(sck, mosi, miso, csn, gdo0, gdo2)
    cc.reset()
    cc.init()
    cc.set_frequency(433.92)

    if decoder_type == "fsk":
        cc.set_modulation("2-FSK")
    else:
        cc.set_modulation("ASK_OOK")

    cc.set_power_level(0)

    print(f"[INFO] Replaying {decoder_type.upper()} payload: {payload}")
    cc.send_data(payload)
    print("[INFO] Playback complete.")
    GPIO.cleanup()

if __name__ == "__main__":
    main()
from softspi import CC1101
import time

cc = CC1101(sck=21, mosi=20, miso=19, csn=18, gdo0=26, gdo2=16)

cc.reset()
cc.init()
cc.set_frequency(433.92)
print("FREQ2:", hex(cc.read_register(0x0D)))
print("FREQ1:", hex(cc.read_register(0x0E)))
print("FREQ0:", hex(cc.read_register(0x0F)))

cc.set_modulation('ASK_OOK')  # or '2-FSK'
cc.set_power_level(0)         # 0 = max, 7 = min

# Replace with your real signal
payload = [0xA2, 0xF1, 0xD0] * 20

# Send in a loop
for _ in range(10):
    cc.send_data(payload)
    print("Signal sent.")
    time.sleep(1)

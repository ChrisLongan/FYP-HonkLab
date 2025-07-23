# Simplified KeeLoq brute-force decryption (educational 16-bit version)
# KeeLoq uses a 528-round NLFSR cipher — this is a reduced demo

NLF = 0x3A5C742E  # Non-linear feedback table (standard KeeLoq)

def keeloq_decrypt(block, key, rounds=528):
    for _ in range(rounds):
        bit31 = (block >> 31) & 1
        bit0  = (block >> 0) & 1
        bit16 = (block >> 16) & 1
        bit1  = (block >> 1) & 1
        bit9  = (block >> 9) & 1
        feedback = bit31 ^ bit0 ^ bit16 ^ bit1 ^ bit9
        block = ((block << 1) | feedback) & 0xFFFFFFFF
    return block ^ key

def bruteforce_keeloq(encrypted_code, known_counter=None):
    print(f"🔐 Encrypted Code: {hex(encrypted_code)}")
    for key in range(0x0000, 0x10000):  # 16-bit keyspace
        decrypted = keeloq_decrypt(encrypted_code, key)
        if known_counter:
            if decrypted == known_counter:
                print(f"[MATCH] Key=0x{key:04X} → Counter={decrypted}")
                return key
        else:
            print(f"Key=0x{key:04X} → Decrypted={hex(decrypted)}")

    print("❌ No match found in 16-bit space.")
    return None

if __name__ == "__main__":
    # Example 32-bit encrypted KeeLoq rolling code (fake/test)
    fake_encrypted = 0x9A1B2C3D
    fake_expected_counter = 0x00001234  # Simulated known counter

    bruteforce_keeloq(fake_encrypted, known_counter=fake_expected_counter)

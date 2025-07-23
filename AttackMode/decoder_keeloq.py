# Warning: This code is currently under development.
#Limitation: 64-bit KeeLoq brute-force takes too much GPU for py, better in C, currenlty running in multiprocessing.
#64-bit key, 528 rounds

import multiprocessing
import time
from decoder_stor import store_decoded_payload

# 64-bit KeeLoq decryption function
def keeloq_decrypt(ciphertext, key, rounds=528):
    NLF = 0x3A5C742E
    result = ciphertext
    for i in range(rounds):
        bit0 = (result >> 0) & 1
        bit16 = (result >> 16) & 1
        bit1 = (result >> 1) & 1
        bit9 = (result >> 9) & 1
        bit20 = (result >> 20) & 1

        nlf_index = (bit0 << 0) | (bit1 << 1) | (bit9 << 2) | (bit16 << 3) | (bit20 << 4)
        feedback_bit = ((result >> 31) & 1) ^ ((NLF >> nlf_index) & 1) ^ ((key >> (i % 64)) & 1)

        result = ((result << 1) | feedback_bit) & 0xFFFFFFFF
    return result

# Worker function
def worker(start_key, end_key, ciphertext, expected_plaintext, return_dict, worker_id):
    for key in range(start_key, end_key):
        decrypted = keeloq_decrypt(ciphertext, key)
        if decrypted == expected_plaintext:
            return_dict["found"] = (key, decrypted)
            return
        if key % 0x100000 == 0:
            print(f"[Worker {worker_id}] Checked key: 0x{key:016X}")
    return_dict[worker_id] = None

# Brute-force with multiprocessing
def multiprocessing_keeloq_bruteforce(ciphertext, expected_plaintext, keyspace_bits=24, num_workers=4):
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    jobs = []

    total_keys = 1 << keyspace_bits
    chunk_size = total_keys // num_workers

    print(f"Starting brute-force in {num_workers} processes...")
    start_time = time.time()

    for i in range(num_workers):
        start_key = i * chunk_size
        end_key = start_key + chunk_size
        p = multiprocessing.Process(target=worker, args=(start_key, end_key, ciphertext, expected_plaintext, return_dict, i))
        jobs.append(p)
        p.start()

    for proc in jobs:
        proc.join()

    elapsed = time.time() - start_time
    if "found" in return_dict:
        key, plain = return_dict["found"]
        hex_val = hex(plain)[2:].zfill(16).upper()
        print(f"✅ Key found: 0x{key:016X} → {hex_val} in {elapsed:.2f} sec")
        store_decoded_payload(hex_val, decoder_type="keeloq")
        return f"✅ Key found: 0x{key:016X} → {hex_val} in {elapsed:.2f} sec"
    else:
        print(f"No key found in {elapsed:.2f} sec")
        return f"No key found in {elapsed:.2f} sec"
    
#untested example:(24-bit space)
# ciphertext = 0x9A1B2C3D
# expected_plaintext = 0x66E2840E
# result = multiprocessing_keeloq_bruteforce(ciphertext, expected_plaintext, keyspace_bits=24, num_workers=4)
# result


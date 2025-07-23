
def store_decoded_payload(decoded_hex, decoder_type="generic"):
    clean_hex = decoded_hex.strip().lower().replace("0x", "").zfill(16)

    # Always append to general log for replay
    with open("decoded_bits.txt", "a") as all_log:
        all_log.write(clean_hex + "\n")

    # Determine per-type log files
    decoder_type = decoder_type.lower()
    if decoder_type not in ["keeloq", "ook", "fsk"]:
        decoder_type = "generic"

    type_log = f"{decoder_type}_decoded.txt"
    type_latest = f"latest_{decoder_type}.txt"

    # Append to per-type log
    with open(type_log, "a") as typelog:
        typelog.write(clean_hex + "\n")

    # Overwrite latest decode
    with open(type_latest, "w") as latest:
        latest.write(clean_hex)

    print(f"[INFO] Stored decoded payload ({decoder_type}): {clean_hex}")

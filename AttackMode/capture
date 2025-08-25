# save as capture_simple_pressline.py
import argparse, time, os
import numpy as np

try:
    from rtlsdr import RtlSdr
except ImportError:
    raise SystemExit("[ERROR] Install pyrtlsdr:  pip install pyrtlsdr")

def nearest_gain(sdr, requested):
    vals = getattr(sdr, "valid_gains_db", [])
    if not vals:
        return float(requested)
    vals = np.array(vals, dtype=float)
    return float(vals[np.argmin(np.abs(vals - float(requested)))])

def main():
    p = argparse.ArgumentParser(description="Simple RTL-SDR IQ capture (single-line prompt)")
    p.add_argument("-f","--freq", type=float, default=433.92, help="MHz (default 433.92)")
    p.add_argument("-s","--samp", type=float, default=2.048, help="MS/s (default 2.048)")
    p.add_argument("-g","--gain", default="auto", help='dB or "auto" (default auto)')
    p.add_argument("-d","--dur",  type=float, default=0.2, help="seconds (default 0.2)")
    p.add_argument("-o","--out",  default=None, help="output .bin (complex64)")
    p.add_argument("--idx", type=int, default=0, help="device index")
    p.add_argument("--pre", type=float, default=1.0, help="standby countdown seconds (default 1.0)")
    args = p.parse_args()

    sdr = RtlSdr(args.idx)
    try:
        sdr.center_freq = args.freq * 1e6
        sdr.sample_rate = args.samp * 1e6
        sdr.set_agc_mode(False)  # disable RTL AGC

        if args.gain == "auto":
            sdr.gain = "auto"
        else:
            g = nearest_gain(sdr, args.gain)
            if str(g) != str(args.gain):
                # keep it one line: show snap info briefly then overwrite
                print(f"\r[i] snapping gain {args.gain} dB -> {g} dB", end="", flush=True)
                time.sleep(0.6)
            sdr.gain = g

        total_samples = int(args.dur * sdr.sample_rate)
        out = args.out or f"iq_{int(sdr.center_freq/1e6)}MHz_{args.dur:.2f}s.bin"

        # --- standby countdown on one updating line ---
        start = time.perf_counter()
        while True:
            now = time.perf_counter()
            rem = args.pre - (now - start)
            if rem <= 0:
                break
            msg = (f"[STANDBY {rem:4.2f}s] Get ready to PRESS key  "
                   f"f={sdr.center_freq/1e6:.3f}MHz  sr={sdr.sample_rate/1e6:.3f}MS/s  "
                   f"gain={sdr.gain}  -> {os.path.basename(out)}")
            print("\r" + msg[:160], end="", flush=True)  # keep line compact
            time.sleep(0.05)

        # --- capture with single-line live progress (PRESS KEY NOW) ---
        captured = 0
        chunk = max(4096, int(sdr.sample_rate * 0.02))  # ~20 ms chunks
        t0 = time.perf_counter()
        with open(out, "wb") as f:
            while captured < total_samples:
                n = min(chunk, total_samples - captured)
                buf = sdr.read_samples(n).astype(np.complex64)
                buf.tofile(f)
                captured += n
                elapsed = captured / sdr.sample_rate
                pct = 100 * captured / total_samples
                msg = (f"[CAPTURE {elapsed:5.3f}/{args.dur:.3f}s  {pct:5.1f}%]  PRESS KEY NOW…  "
                       f"-> {os.path.basename(out)}")
                print("\r" + msg[:160], end="", flush=True)

        size_mb = os.path.getsize(out) / 1e6
        # overwrite line with final status and newline
        done = (f"[DONE] Saved {os.path.basename(out)} ({size_mb:.2f} MB)  "
                f"f={sdr.center_freq/1e6:.3f}MHz  sr={sdr.sample_rate/1e6:.3f}MS/s  gain={sdr.gain}        ")
        print("\r" + done + " " * 10)  # pad to clear remnants
        print()  # final newline

    finally:
        sdr.close()

if __name__ == "__main__":
    main()

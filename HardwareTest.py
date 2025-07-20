import time
import spidev
import subprocess
import sys

def check_cc1101():
    """Check for CC1101 on SPI1"""
    print("🔍 Checking for CC1101 on SPI1...")
    spi = None
    try:
        spi = spidev.SpiDev()
        spi.open(1, 0)  # SPI1, CE0
        spi.max_speed_hz = 500000
        spi.mode = 0
        time.sleep(0.1)
        
        # Read PARTNUM register (0x30)
        partnum = spi.xfer2([0x30 | 0x80, 0x00])[1]
        # Read VERSION register (0x31) 
        version = spi.xfer2([0x31 | 0x80, 0x00])[1]
        
        # CC1101 should have PARTNUM = 0x00 and VERSION should be valid (not 0x00 or 0xFF)
        if partnum == 0x00 and version not in [0x00, 0xFF]:
            print(f"✅ CC1101 detected — PARTNUM: 0x{partnum:02X}, VERSION: 0x{version:02X}")
            return True
        else:
            print(f"⚠️ CC1101 not detected or miswired — PARTNUM: 0x{partnum:02X}, VERSION: 0x{version:02X}")
            return False
            
    except PermissionError:
        print("❌ Permission denied. Try running with sudo or check SPI permissions.")
        return False
    except FileNotFoundError:
        print("❌ SPI device not found. Is SPI enabled in raspi-config?")
        return False
    except Exception as e:
        print(f"❌ SPI communication error with CC1101: {e}")
        return False
    finally:
        # Always close SPI connection
        if spi:
            try:
                spi.close()
            except:
                pass

def check_rtlsdr():
    """Check for RTL-SDR with improved error handling and timeout."""
    print("\n🔍 Checking for RTL-SDR...")
    try:
        # Add timeout to prevent hanging
        output = subprocess.check_output(
            ['rtl_test', '-t'], 
            stderr=subprocess.STDOUT, 
            text=True,
            timeout=10
        )
        
        if "Found 1 device" in output:
            print("✅ RTL-SDR detected and working.")
            return True
        elif "No supported devices found" in output:
            print("⚠️ No RTL-SDR devices found. Check USB connection.")
            return False
        else:
            print("⚠️ RTL-SDR check completed but status unclear.")
            print(f"Output: {output.strip()}")
            return False
            
    except FileNotFoundError:
        print("❌ rtl_test tool not found. Install with: sudo apt install rtl-sdr")
        return False
    except subprocess.TimeoutExpired:
        print("❌ rtl_test timed out. Device may be in use or unresponsive.")
        return False
    except subprocess.CalledProcessError as e:
        print("❌ rtl_test returned an error:")
        print(e.output.strip())
        return False

def main():
    """Main test function with summary."""
    print("🧪 Hardware Self-Test Starting...\n")
    
    results = {}
    results['cc1101'] = check_cc1101()
    results['rtlsdr'] = check_rtlsdr()
    
    print("\n" + "="*40)
    print("📋 SUMMARY:")
    print(f"CC1101:  {'✅ PASS' if results['cc1101'] else '❌ FAIL'}")
    print(f"RTL-SDR: {'✅ PASS' if results['rtlsdr'] else '❌ FAIL'}")
    
    if all(results.values()):
        print("\n🎉 All hardware tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️  Some hardware tests failed. Check connections and setup.")
        sys.exit(1)

if __name__ == "__main__":
    main()
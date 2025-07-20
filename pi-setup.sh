#!/bin/bash

echo "Starting Raspberry Pi setup for Automotive RF Toolkit..."

# Prevent re-running setup
SETUP_FLAG="/home/pi/.rke_setup_done"
if [ -f "$SETUP_FLAG" ]; then
    echo "Setup already completed. Skipping..."
    exit 0
fi

# Exit safely if not on a Raspberry Pi
if ! uname -a | grep -qi "raspberrypi"; then
    echo "❌ Not a Raspberry Pi — aborting setup to prevent OS damage."
    mv pi-setup.sh pi-setup.txt && echo "Renamed this script to 'pi-setup.txt'."
    exit 1
fi

echo "✅ Raspberry Pi detected. Proceeding..."

# ---------------------------------------------
# System dependencies (do NOT full-upgrade)
# ---------------------------------------------
echo "📦 Updating package lists..."
sudo apt update

echo "📦 Installing system dependencies..."
sudo apt install -y \
  python3-pip \
  python3-spidev \
  python3-rpi.gpio \
  git \
  build-essential \
  rtl-sdr \
  cmake \
  libusb-1.0-0-dev \
  libfftw3-dev

if [ $? -ne 0 ]; then
    echo "❌ Package installation failed. Exiting..."
    exit 1
fi

# ---------------------------------------------
# RTL-SDR: Blacklist kernel TV driver
# ---------------------------------------------
echo "🔧 Configuring RTL-SDR..."
BLACKLIST_FILE="/etc/modprobe.d/no-rtl.conf"
if ! grep -q "dvb_usb_rtl28xxu" "$BLACKLIST_FILE" 2>/dev/null; then
    echo "blacklist dvb_usb_rtl28xxu" | sudo tee "$BLACKLIST_FILE"
    echo "✅ RTL-SDR kernel driver blacklisted."
else
    echo "✔️ RTL-SDR driver already blacklisted."
fi

# ---------------------------------------------
# Python packages from requirements.txt
# ---------------------------------------------
if [ -f "Requirement.txt" ]; then
    echo "📦 Installing Python packages..."
    pip3 install -r Requirement.txt
    if [ $? -ne 0 ]; then
        echo "⚠️ Some Python packages failed to install, but continuing..."
    fi
else
    echo "⚠️ Requirement.txt not found. Skipping pip installs."
fi

# ---------------------------------------------
# Enable SPI1 (for CC1101)
# ---------------------------------------------
echo "🔧 Configuring SPI..."
CONFIG_FILE="/boot/config.txt"
NEEDS_REBOOT=false

if ! grep -q "dtoverlay=spi1-3cs" "$CONFIG_FILE"; then
    echo "🔧 Enabling SPI1 overlay..."
    echo "dtoverlay=spi1-3cs" | sudo tee -a "$CONFIG_FILE"
    NEEDS_REBOOT=true
    echo "✅ SPI1 overlay added."
else
    echo "✔️ SPI1 already enabled."
fi

# ---------------------------------------------
# Mark setup as complete (THIS WAS MISSING!)
# ---------------------------------------------
echo "✅ Creating setup completion flag..."
touch "$SETUP_FLAG"
echo "$(date): Setup completed successfully" > "$SETUP_FLAG"

echo ""
echo "🎉 Setup complete!"

if [ "$NEEDS_REBOOT" = true ]; then
    echo ""
    echo "⚠️  REBOOT REQUIRED to activate SPI1 changes."
    echo "Run: sudo reboot"
else
    echo "✔️ No reboot needed - all configurations were already in place."
fi

echo ""
echo "To verify hardware after reboot, run your hardware test script."


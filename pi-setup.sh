#!/bin/bash

echo "Starting Raspberry Pi setup for Automotive RF Toolkit..."

# 🛡️ Exit safely if not on a Raspberry Pi
if ! uname -a | grep -qi "raspberrypi"; then
    echo " Not a Raspberry Pi — aborting setup to prevent OS damage."
    mv pi-setup.sh pi-setup.txt && echo "Renamed this script to 'pi-setup.txt'."
    exit 1
fi

echo "✅ Raspberry Pi detected. Proceeding..."

# ---------------------------------------------
# System dependencies (do NOT full-upgrade)
# ---------------------------------------------
sudo apt update
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

# ---------------------------------------------
# RTL-SDR: Blacklist kernel TV driver
# ---------------------------------------------
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
if [ -f "requirements.txt" ]; then
    echo "📦 Installing Python packages..."
    pip3 install -r requirements.txt
else
    echo "⚠️ requirements.txt not found. Skipping pip installs."
fi

# ---------------------------------------------
# Enable SPI1 (for CC1101)
# ---------------------------------------------
CONFIG_FILE="/boot/config.txt"
if ! grep -q "dtoverlay=spi1-3cs" "$CONFIG_FILE"; then
    echo "🔧 Enabling SPI1 overlay..."
    echo "dtoverlay=spi1-3cs" | sudo tee -a "$CONFIG_FILE"
    echo "🔁 Please reboot to activate SPI1."
else
    echo "✔️ SPI1 already enabled."
fi

echo "✅ Setup complete! Please reboot if this is the first time."



# ---------------------------------------------
# Using on Pi
# ---------------------------------------------
chmod +x pi-setup.sh
./pi-setup.sh
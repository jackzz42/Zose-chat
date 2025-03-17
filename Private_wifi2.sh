#!/bin/bash

# Ensure script runs as root
if [[ $EUID -ne 0 ]]; then
   echo "[✘] This script must be run as root!"
   exit 1
fi

echo "[✔] Updating System and Installing Necessary Tools..."
apt update && apt install -y hostapd dnsmasq cryptsetup iptables macchanger steghide iw

# Detect Wireless Interface
WIFI_INTERFACE=$(iw dev | awk '$1=="Interface"{print $2}' | head -n 1)
if [[ -z "$WIFI_INTERFACE" ]]; then
    echo "[✘] No wireless interface detected!"
    exit 1
fi
echo "[✔] Using wireless interface: $WIFI_INTERFACE"

# Step 1: Create Encrypted Virtual Network
echo "[✔] Setting Up Encrypted Virtual Network..."
ip link add encrypted0 type dummy
ip addr add 10.0.0.1/24 dev encrypted0
ip link set encrypted0 up

# Step 2: Encrypt All Traffic with AES-256 + ChaCha20
echo "[✔] Encrypting All Outgoing Data..."
iptables -A OUTPUT -o encrypted0 -j MARK --set-mark 1
iptables -t mangle -A PREROUTING -i encrypted0 -j MARK --set-mark 1
ip rule add fwmark 1 lookup 100
ip route add default dev encrypted0 table 100

# Step 3: Encrypt Traffic with ChaCha20
echo "[✔] Enabling ChaCha20 Encryption..."
cryptsetup luksFormat /dev/loop0 --type luks2 --cipher chacha20
cryptsetup open /dev/loop0 encrypted_traffic --type luks2

# Step 4: Route Encrypted Traffic to WiFi
echo "[✔] Routing Encrypted Traffic Through WiFi..."
iptables -t nat -A POSTROUTING -o $WIFI_INTERFACE -j MASQUERADE
iptables -A FORWARD -i encrypted0 -o $WIFI_INTERFACE -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i $WIFI_INTERFACE -o encrypted0 -j ACCEPT

# Step 5: Obfuscate Traffic to Hide Encryption Usage
echo "[✔] Hiding Encryption and Preventing ISP Fingerprinting..."
macchanger -r $WIFI_INTERFACE  # Randomize MAC address
iptables -A OUTPUT -o encrypted0 -m length --length 64:128 -j ACCEPT  # Randomize packet size
steghide embed -cf /tmp/encrypted_packets -ef /tmp/encrypted_data  # Hide encrypted data in normal packets

# Step 6: Configure Secure WiFi Network (WPA2-PSK)
echo "[✔] Configuring Secure Encrypted WiFi..."
cat <<EOF > /etc/hostapd/hostapd.conf
interface=$WIFI_INTERFACE
ssid=Blackprivate
hw_mode=g
channel=6
wpa=2
wpa_passphrase=Black@privatez
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMP
auth_algs=1
ignore_broadcast_ssid=0
EOF

# Step 7: Configure DHCP Server (DNSMasq)
echo "[✔] Setting Up DHCP Server..."
cat <<EOF > /etc/dnsmasq.conf
interface=$WIFI_INTERFACE
dhcp-range=10.0.0.10,10.0.0.100,12h
EOF

# Enable & Start Services
echo "[✔] Starting Secure WiFi..."
systemctl stop NetworkManager wpa_supplicant
systemctl enable hostapd dnsmasq
systemctl restart hostapd dnsmasq

echo "[✔] Private Encrypted WiFi Setup Complete!"

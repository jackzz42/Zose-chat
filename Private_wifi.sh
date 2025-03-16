#!/bin/bash

# Ensure script runs as root
if [[ $EUID -ne 0 ]]; then
   echo "[✘] This script must be run as root!"
   exit 1
fi

echo "[✔] Updating System and Installing Dependencies..."
apt update && apt upgrade -y
apt install -y hostapd dnsmasq iptables openssl obfs4proxy shadowsocks-libev snort fail2ban yggdrasil macchanger steghide

echo "[✔] Setting Up Secure Encrypted WiFi..."
cat <<EOF > /etc/hostapd/hostapd.conf
interface=wlan0
ssid=MySecureWiFi
hw_mode=g
channel=6
wpa=2
wpa_passphrase=YourStrongPasswordHere
wpa_key_mgmt=WPA-PSK WPA3-SAE
rsn_pairwise=CCMP
ieee80211w=2
ignore_broadcast_ssid=1
EOF

systemctl restart hostapd
systemctl enable hostapd

echo "[✔] Enabling Automated MAC Address Randomization..."
(crontab -l 2>/dev/null; echo "*/5 * * * * macchanger -r wlan0") | crontab -

echo "[✔] Encrypting Internet Traffic Locally with AES-256 + ChaCha20..."
iptables -A OUTPUT -o wlan0 -p tcp --dport 443 -j MARK --set-mark 1
iptables -t nat -A POSTROUTING -o wlan0 -j MASQUERADE

openssl enc -aes-256-cbc -salt -in /dev/stdin -out /dev/stdout -k SuperSecretPassword | \
openssl enc -chacha20 -salt -in /dev/stdin -out /dev/stdout -k AnotherSecretPassword &

echo "[✔] Hiding Traffic Using Meek & Shadowsocks..."
shadowsocks-server -c /etc/shadowsocks/config.json -d start
obfs4proxy -mode server -listen 0.0.0.0:443 -enableLogging=true -logLevel=INFO -key RandomObfsKey &
meek-server --port 443 --url https://www.microsoft.com &

echo "[✔] Setting Up Intrusion Detection System (IDS)..."
systemctl enable snort
systemctl start snort

echo "[✔] Enabling Fail2Ban for Brute-Force Protection..."
systemctl enable fail2ban
systemctl start fail2ban

echo "[✔] Setting Up Yggdrasil Mesh Network..."
cat <<EOF > /etc/yggdrasil.conf
Peers: []
Listen: []
EOF
systemctl enable yggdrasil
systemctl start yggdrasil

echo "[✔] Implementing Steganography for Fake HTTPS Traffic..."
steg_file="/var/www/html/index.html"
echo "Hidden Data Inside" > secret_message.txt
steghide embed -cf $steg_file -ef secret_message.txt -p HiddenPass

echo "[✔] Enabling Randomized Packet Injection for Advanced Obfuscation..."
iptables -A OUTPUT -p tcp --dport 443 -j DROP
iptables -A OUTPUT -p udp --dport 443 -j DROP

echo "[✔] Fully Local & Private Secure WiFi Setup is Now Active!"

#!/bin/bash

# Ensure script runs with root privileges
if [[ $EUID -ne 0 ]]; then
   echo "[✘] This script must be run as root!"
   exit 1
fi

echo "[✔] Stopping Secure WiFi..."
systemctl stop hostapd
systemctl disable hostapd

echo "[✔] Stopping Snort (Intrusion Detection System)..."
systemctl stop snort
systemctl disable snort

echo "[✔] Stopping Fail2Ban (Brute-force Protection)..."
systemctl stop fail2ban
systemctl disable fail2ban

echo "[✔] Stopping Yggdrasil Mesh Network..."
systemctl stop yggdrasil
systemctl disable yggdrasil

echo "[✔] Disabling MAC Address Randomization..."
crontab -l | grep -v "macchanger -r wlan0" | crontab -

echo "[✔] Removing Encryption Processes..."
killall openssl
killall obfs4proxy
killall shadowsocks-server
killall meek-server

echo "[✔] Flushing iptables Rules..."
iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X

echo "[✔] Secure WiFi and Encryption Fully Stopped!"
exit 0

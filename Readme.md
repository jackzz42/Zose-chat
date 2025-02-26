
# SecureChat - Encrypted P2P Communication with Tor & I2P

SecureChat is a **fully encrypted**, **peer-to-peer** messaging application with **WebSockets**, **AES-256 encryption**, and **Tor/I2P support** for **anonymous and secure communication**.

## Features
✔ **End-to-End Encryption (AES-256 & Argon2 hashing)** – All messages are encrypted before transmission.  
✔ **WebSockets Security (HMAC authentication, TLS encryption)** – Ensures message integrity.  
✔ **Tor & I2P Routing** – Enables anonymous and untraceable communication.  
✔ **P2P Direct Messaging** – No central server; all communication is peer-to-peer.  
✔ **Secure File Sharing** – Encrypted file transfers using AES-256 and ECDH.  
✔ **One-Time Secure Login Links** – Temporary access URLs to prevent unauthorized logins.  
✔ **Multi-layer Authentication** – Password + device fingerprinting for enhanced security.  
✔ **Metadata Anonymization** – Removes tracking data from messages and files.  

---

## 1. Installation

### Using venv (Recommended)
\`\`\`sh
# Create a virtual environment
python -m venv venv  

# Activate the virtual environment  
# On Linux/Mac:
source venv/bin/activate  
# On Windows:
venv\Scripts\activate  

# Install dependencies
pip install -r requirements.txt  
\`\`\`

---

### Using pipx
\`\`\`sh
pip install --user pipx  
pipx install secure-chat  
\`\`\`

---

## 2. Running SecureChat

### Start the Web Chat
\`\`\`sh
python main.py  
\`\`\`

### Start the Terminal Chat
\`\`\`sh
python start_chat.py  
\`\`\`

---

## 3. Enabling Tor & I2P for Anonymous Communication

### Tor Setup
1. **Install Tor**  
   - **Linux:** \`sudo apt install tor\`  
   - **Mac:** \`brew install tor\`  
   - **Windows:** Download [Tor Expert Bundle](https://www.torproject.org/download/)  

2. **Start Tor**
   \`\`\`sh
   tor &
   \`\`\`

3. **Configure torrc to allow SOCKS proxy**  
   - Default Proxy: \`127.0.0.1:9050\`  

4. **Modify SecureChat config.json to use Tor**
   \`\`\`json
   {
       "use_tor": true,
       "proxy": "socks5h://127.0.0.1:9050"
   }
   \`\`\`

---

### I2P Setup
1. **Install I2P**  
   - **Linux:** \`sudo apt install i2pd\`  
   - **Mac:** \`brew install i2pd\`  
   - **Windows:** Download from [geti2p.net](https://geti2p.net/)  

2. **Start I2P**
   \`\`\`sh
   i2pd --daemon
   \`\`\`

3. **Modify SecureChat config.json to use I2P**
   \`\`\`json
   {
       "use_i2p": true,
       "proxy": "http://127.0.0.1:4444"
   }
   \`\`\`

---

## 4. Secure File Sharing
SecureChat allows encrypted file transfers using **AES-256 and ECDH** to ensure privacy.

- Files are **encrypted locally** before being sent.  
- **Metadata is removed** to prevent tracking.  
- **Temporary decryption keys** are used to avoid exposure.  

**To send an encrypted file:**
\`\`\`sh
python send_file.py --file yourfile.txt
\`\`\`

**To receive and decrypt a file:**
\`\`\`sh
python receive_file.py --key your-decryption-key
\`\`\`

---

## 5. Security Measures
✅ **End-to-End Encryption** – Messages are encrypted before sending and decrypted only by the recipient.  
✅ **Anonymous Routing** – Messages are routed through **Tor/I2P** to hide IP addresses.  
✅ **Self-Destructing Messages** – Option to delete messages after a set time.  
✅ **Anti-MITM Protection** – WebSocket messages include HMAC authentication.  
✅ **Secure Login System** – One-time login URLs prevent brute-force attacks.  

---

## 6. Troubleshooting
**Problem:** WebSocket connection fails.  
✅ **Solution:** Ensure Tor/I2P is running and configured in \`config.json\`.  

**Problem:** SecureChat is not encrypting messages.  
✅ **Solution:** Check \`encryption.log\` for errors and verify \`cryptography\` package is installed.  

**Problem:** Messages are not being delivered.  
✅ **Solution:** Ensure peers are connected and not behind restrictive firewalls.  

---

## 7. License
SecureChat is **open-source software** licensed under the **MIT License**.

EOF

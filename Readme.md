

# **SecureChat - Encrypted P2P Communication with Tor & I2P**

SecureChat is a **fully encrypted**, **peer-to-peer (P2P)** messaging application with **WebSockets**, **AES-256 encryption**, and **Tor/I2P support** for **anonymous and secure communication**.



## **Features**
- ✅ **End-to-End Encryption (AES-256 & Argon2 hashing)** – Messages are encrypted before transmission.  
- ✅ **WebSockets Security (HMAC authentication, TLS encryption)** – Ensures message integrity.  
- ✅ **Tor & I2P Routing** – Enables anonymous and untraceable communication.  
- ✅ **P2P Direct Messaging** – No central server; all communication is peer-to-peer.  
- ✅ **Secure File Sharing** – Encrypted file transfers using AES-256 and ECDH.  
- ✅ **One-Time Secure Login Links** – Temporary access URLs to prevent unauthorized logins.  
- ✅ **Multi-layer Authentication** – Password + device fingerprinting for enhanced security.  
- ✅ **Metadata Anonymization** – Removes tracking data from messages and files.  



## **Installation**

### **Using `venv` (Recommended)**
```sh
# Create a virtual environment
python -m venv venv  
```
# Activate the virtual environment  
# On Linux/Mac:
source venv/bin/activate  
# On Windows:
venv\Scripts\activate  

# Install dependencies
pip install -r requirements.txt



Using pipx

# Install pipx if not already installed
python -m pip install --user pipx  
python -m pipx ensurepath  

# Restart terminal if necessary, then install SecureChat
pipx install secure-chat




Running SecureChat

Start the Web Chat

python main.py

Start the Terminal Chat

python start_chat.py




Enabling Tor & I2P for Anonymous Communication

Tor Setup

# Install Tor
# Linux:
sudo apt install tor  

# Mac:
brew install tor  

# Windows: 
# Download Tor Expert Bundle from https://www.torproject.org/download/

# Start Tor
tor &

Modify torrc to allow SOCKS proxy

# Default Proxy:
127.0.0.1:9050

Modify SecureChat config.json to use Tor

{
    "use_tor": true,
    "proxy": "socks5h://127.0.0.1:9050"
}


---

I2P Setup

# Install I2P
# Linux:
sudo apt install i2pd  

# Mac:
brew install i2pd  

# Windows: 
# Download from https://geti2p.net/

# Start I2P
i2pd --daemon

Modify SecureChat config.json to use I2P

{
    "use_i2p": true,
    "proxy": "http://127.0.0.1:4444"
}


---

Security Considerations

Ensure Tor/I2P is running before chatting to keep communication anonymous.

Never share session keys or private keys outside SecureChat.

Use strong passwords and store them securely.

Monitor logs for suspicious activity.

Run SecureChat on a secure machine to prevent local exploits.




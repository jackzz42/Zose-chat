# ZOSE - Secure Encrypted Chat System

🚀 **ZOSE is a highly secure real-time chat system with end-to-end encryption, metadata protection, and Perfect Forward Secrecy.**

## 🔐 Features & Security

✅ **End-to-End Encryption** (AES-GCM, ChaCha20, AES-256 CBC)  
✅ **Perfect Forward Secrecy** (ECC-P521 & X25519 Key Exchange)  
✅ **HMAC-SHA256** for Message Integrity Protection  
✅ **Argon2id** for Secure Password Hashing  
✅ **WebSockets Secured with WSS**  
✅ **Rate Limiting** (Brute Force Protection)  
✅ **SQL Injection Protection** (Sanitized Inputs)  
✅ **Encrypted Logging** (AES-256 + HMAC Integrity)  

---

## ⚙ Installation

### **1. Install Required Dependencies**

```bash
pip install -r requirements.txt
```

### **2. Set Up Environment Variables**  
Create a `.env` file in the project directory and add:  
```
SESSION_SECRET=your_secure_random_key_here
```

### **3. Run the Server**  
```bash
python main.py
```

### **4. Access the Chat Interface**  
- **Web Interface:** `https://localhost:5000`  
- **Terminal Interface:**  
  ```bash
  python cli_chat.py --username YOUR_NAME --room ROOM_ID --cipher aes-gcm
  ```

---

## 🔧 **Security Details**

| Security Feature       | Algorithm | Security Level |
|-----------------------|-----------|----------------|
| **Message Encryption** | AES-GCM, ChaCha20 | **128-bit to 256-bit** |
| **Key Exchange** | ECC P-521, X25519 | **256-bit Security** |
| **Password Hashing** | Argon2id | **Resistant to Brute Force** |
| **Message Integrity** | HMAC-SHA256 | **Prevents Tampering** |
| **Logging Security** | AES-256 + HMAC | **Encrypted & Tamper-Proof** |

---

## 📜 License

ZOSE is an open-source project. Feel free to modify and contribute!  

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
✅ **Secure File Sharing** (AES-256 Encrypted Uploads)  
✅ **Admin Panel** (User Management, Ban/Kick, Monitor Security Logs)  

---

## ⚙ Installation & Setup (For All OS)

### **🔹 1. Install Python (if not installed)**
- **Windows**: Download and install Python from [python.org](https://www.python.org/).  
- **Linux/macOS**: Python is pre-installed. Verify with:  
  ```bash
  python3 --version
  ```

### **🔹 2. Clone or Download ZOSE**
```bash
git clone https://github.com/your-repo/ZOSE-Secure-Chat.git
cd ZOSE-Secure-Chat
```

### **🔹 3. Set Up Virtual Environment (Recommended)**
```bash
python3 -m venv zose_env
source zose_env/bin/activate  # On macOS/Linux
zose_env\Scripts\activate   # On Windows
```

### **🔹 4. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **🔹 5. Set Up Environment Variables**  
Create a `.env` file in the project directory and add:  
```
SESSION_SECRET=your_secure_random_key_here
```

### **🔹 6. Run the Server**  
```bash
python main.py
```

### **🔹 7. Access the Chat Interface**  
- **Web Interface:** `https://localhost:5000`  
- **Terminal Interface:**  
  ```bash
  python cli_chat.py --username YOUR_NAME --room ROOM_ID --cipher aes-gcm
  ```

---

## 🛠 **Admin Panel & User Management**
- The **room creator automatically becomes the admin**.  
- Admins can:  
  ✅ **Ban/Kick users**  
  ✅ **View live user logs**  
  ✅ **Monitor security events**  
  ✅ **Shut down the chat room securely**  

To access the admin panel:  
```  
https://localhost:5000/admin  
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

## 🖥 **UI Overview**
### **1️⃣ Home Page (`index.html`)**
- Users can **Create a Room** or **Join an Existing Room**.  
- **Encryption selection**: AES-GCM, ChaCha20, or AES-256.  
- **Dark Theme & Responsive UI**.  

### **2️⃣ Chat Room Page (`room.html`)**
- **Real-time encrypted chat** (WebSocket-based).  
- **User list panel** (Shows connected users).  
- **Secure File Sharing** (AES-256 encrypted file uploads).  
- **Ban/Kick users option for the host**.  

### **3️⃣ Admin Panel (`/admin`)**
- View Active Users.  
- Monitor security logs.  
- Ban/kick users.  
- Shut down the room securely.  

---

## 📂 **How Secure File Sharing Works**
✅ **Files are AES-256 encrypted before upload**.  
✅ **Only users with the correct key can decrypt the file**.  
✅ **Files are automatically deleted after a set time**.  

---

## 🖥 **Running ZOSE on Different Operating Systems**
### **Windows**
```bash
python -m venv zose_env
zose_env\Scripts\activate
pip install -r requirements.txt
python main.py
```

### **Linux/macOS**
```bash
python3 -m venv zose_env
source zose_env/bin/activate
pip install -r requirements.txt
python main.py
```

---

## 📜 License

ZOSE is an open-source project. Feel free to modify and contribute!  

<img width="454" height="286" alt="Screenshot 2026-07-13 141922" src="https://github.com/user-attachments/assets/fd415983-42b6-4e42-bae9-7feccb057cf8" />
<img width="1284" height="305" alt="Screenshot 2026-07-13 141740" src="https://github.com/user-attachments/assets/1e18a653-121f-4222-8aec-64fb71fceb3b" />
<img width="700" height="658" alt="Screenshot 2026-07-13 141726" src="https://github.com/user-attachments/assets/5257a647-dddb-45c6-bb7b-54ee8b27bc38" />
<img width="1289" height="306" alt="Screenshot 2026-07-13 141641" src="https://github.com/user-attachments/assets/56817595-1129-49d2-b5bd-32e599e6d1b6" />
<img width="1225" height="767" alt="Screenshot 2026-07-13 141425" src="https://github.com/user-attachments/assets/a7962ddc-4ef5-4322-b26c-472e4fa6e6bd" />
<img width="1919" height="992" alt="Screenshot 2026-07-13 141324" src="https://github.com/user-attachments/assets/695a2d46-00e2-4bc2-8708-937b158ba909" />
<img width="1917" height="976" alt="Screenshot 2026-07-13 141307" src="https://github.com/user-attachments/assets/c0b5d1a9-c61c-49eb-af44-b31e38520d47" />
# 🔐 SecureVault — File Encryption & Digital Signature Platform

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0.3-black?style=for-the-badge&logo=flask&logoColor=white)
![AES-256](https://img.shields.io/badge/AES--256--CBC-Encryption-2563EB?style=for-the-badge&logo=letsencrypt&logoColor=white)
![RSA](https://img.shields.io/badge/RSA--2048-Digital%20Signatures-6D28D9?style=for-the-badge&logo=gnuprivacyguard&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)

> A web-based file security platform that lets you **encrypt files with AES-256**, **sign them with RSA-2048 digital signatures**, verify integrity, and **share securely using decryption codes** — all from a clean browser interface.

🌐 **Live Demo** → [securevault.onrender.com](https://securevault.onrender.com)

---

## ✨ Features

### 🛡️ AES-256 File Encryption
- Password-based **AES-256-CBC** encryption
- **PBKDF2-HMAC-SHA256** key derivation (200,000 iterations)
- Random salt + IV per file — each encryption is unique
- Decrypt instantly with the correct password

### ✍️ RSA-2048 Digital Signatures
- Generate a personal **RSA-2048 key pair** per account
- Sign any file with your **private key**
- Anyone can verify authenticity using your **public key**
- Detects tampering — even a single byte change fails verification

### 🔍 Integrity Verification
- One-click verify — instantly know if a file was modified
- ✅ **Signature VALID** — file is authentic and untampered
- ❌ **Signature INVALID** — file may have been tampered with

### 🔗 Secure File Sharing
- Generate an **8-character share code** when encrypting
- Share the code + password with anyone — no account needed
- Recipient visits `/share`, enters code + password, downloads the decrypted file
- Codes expire after **7 days** with a max of **10 downloads**
- Revoke share codes at any time from your dashboard

### 📂 File Manager Dashboard
- Upload, encrypt, decrypt, sign, verify, rename, and delete files
- Supports: PDF, TXT, PNG, JPG, DOCX, XLSX, ZIP, PY, JSON, CSV, **MP4, MKV, AVI, MOV, MP3, WAV** (up to 500MB)
- Stats cards: Total Files, Encrypted, Signed, Plain
- Doughnut chart showing file security overview
- Live file search and drag-and-drop upload

### 👤 User Authentication
- Secure registration and login
- Passwords hashed with **Werkzeug PBKDF2**
- Per-user file isolation — each user's files are private
- Session-based auth with Flask-Login

### 🎨 Modern UI
- Beautiful **glassmorphism** cards with animated gradient background
- **Dark / Light mode** toggle with saved preference
- **Custom cursor** — glowing dot + ring with hover/click effects
- Fully **responsive** — desktop, tablet, mobile
- Password strength meter on register and encrypt
- Public key viewer with copy & download

---

## 📸 Preview

```
┌─────────────────────────────────────────────┐
│  🔐 SecureVault                      🌙 ☀️  │
├─────────────────────────────────────────────┤
│  📂 4 Files  🔒 2 Encrypted  ✍️ 1 Signed   │
├─────────────────────────────────────────────┤
│  filename.pdf    🔒 Encrypt  ✍️ Sign  ⬇️    │
│  report.pdf.enc  🔓 Decrypt  🔗 Share  ⬇️  │
└─────────────────────────────────────────────┘
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Mdgouse123/SecureVault.git
cd SecureVault

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python app.py
```

### Open in browser
```
http://localhost:5000
```

Register an account and start encrypting files immediately.

---

## 🏗️ Project Structure

```
SecureVault/
├── app.py                  # Flask app + all 16 routes
├── extensions.py           # SQLAlchemy + LoginManager
├── requirements.txt        # Dependencies
├── Procfile                # Gunicorn for deployment
├── modules/
│   ├── encryption.py       # AES-256-CBC encrypt/decrypt
│   ├── signature.py        # RSA-2048 sign/verify
│   └── auth.py             # User + ShareToken models
├── templates/
│   ├── base.html           # Navbar, sidebar, flash messages
│   ├── index.html          # Landing page with features
│   ├── login.html          # Login form
│   ├── register.html       # Register form
│   ├── dashboard.html      # File manager + modals
│   ├── share.html          # Public file access page
│   └── sitemap.xml         # SEO sitemap
├── static/
│   ├── css/style.css       # Full UI with dark mode
│   └── js/main.js          # Cursor, modals, charts, strength
├── uploads/                # Per-user uploaded files (gitignored)
└── keys/                   # RSA key pairs (gitignored)
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, Flask 3.0.3 |
| Database | SQLite + Flask-SQLAlchemy |
| Auth | Flask-Login, Werkzeug PBKDF2 |
| Encryption | cryptography (AES-256-CBC, PBKDF2) |
| Signatures | cryptography (RSA-2048, PSS padding) |
| Frontend | HTML5, CSS3, JavaScript |
| Deployment | Gunicorn on Render |

---

## 🔐 Cryptography Details

| Feature | Algorithm | Details |
|---|---|---|
| File Encryption | AES-256-CBC | 32-byte key, random 16-byte IV and salt per file |
| Key Derivation | PBKDF2-HMAC-SHA256 | 200,000 iterations, 16-byte random salt |
| Digital Signature | RSA-2048 + PSS | SHA-256 hash, MGF1, MAX_LENGTH salt |
| Password Storage | PBKDF2 (Werkzeug) | Secure hash, never stored in plain text |
| Share Tokens | secrets.token_hex | Cryptographically secure 8-character codes |

---

## 📋 Requirements

```
flask==3.0.3
flask-login==0.6.3
flask-sqlalchemy==3.1.1
cryptography==42.0.8
werkzeug==3.0.3
gunicorn==22.0.0
```

---

## 🎯 How to Use — Step by Step

### Encrypt a File
1. Upload a file from the dashboard
2. Click **🔒 Encrypt** → Enter a strong password
3. Optionally check **Generate Share Code** to create a shareable link
4. File is encrypted and saved as `filename.enc`

### Decrypt a File
1. Click **🔓 Decrypt** on any `.enc` file
2. Enter the same password used to encrypt
3. Original file is restored

### Sign a File
1. Click **⚙️ Generate RSA Keys** (first time only)
2. Click **✍️ Sign** on any plain file
3. A `.sig` signature file is created alongside it

### Verify a File
1. Click **🔍 Verify** on any signed file
2. ✅ Valid — file is authentic
3. ❌ Invalid — file was modified after signing

### Share a File
1. Encrypt a file with **Generate Share Code** checked
2. Copy the 8-character code shown in the flash message
3. Share the code + password with anyone
4. They visit `yoursite.com/share`, enter both, and download

---

## 🌐 Deployment

The app is deployed on **Render** (free tier):

👉 [securevault.onrender.com](https://securevault.onrender.com)

> **Note:** Free tier spins down after 15 minutes of inactivity. First visit may take 30–60 seconds.

To deploy your own instance:
1. Push to GitHub
2. Connect repo to [render.com](https://render.com)
3. Set **Start Command**: `gunicorn app:app`
4. Set environment variable: `SECRET_KEY=your-secret-key`

---

## 🔒 Security Notes

- Uploaded files are stored **per-user** in isolated directories
- RSA **private keys** are stored on the server (never exposed)
- Share tokens use **cryptographically secure random generation**
- All passwords are hashed — never stored in plain text
- `uploads/` and `keys/` directories are excluded from git

---

## 👨‍💻 Built By

**Mahamad Gouse N**
Computer Science Engineering Student | Cybersecurity | Python Developer
Alva's Institute of Engineering and Technology, Mangalore

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/mahamad-gouse-n)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=for-the-badge&logo=github)](https://github.com/Mdgouse123)
[![Email](https://img.shields.io/badge/Email-Contact-D14836?style=for-the-badge&logo=gmail)](mailto:mohamedgouse313@gmail.com)
[![Resume](https://img.shields.io/badge/Resume-View-1565C0?style=for-the-badge&logo=googlechrome)](https://mdgouse123.github.io/my-resume/)

---

## 📄 License

This project is licensed under the MIT License.

---

> ⭐ If you found this project useful, please star it on GitHub!

# 📬 Gmail Inbox Cleaner

A simple yet powerful Python-based tool with a user-friendly **Tkinter GUI** to help you clean up your Gmail inbox by identifying top senders and mass-deleting their emails — with optional filters like keywords and date ranges.

---

## ✨ Features

- 🔍 **Scan Top N Senders** from your inbox  
- ✅ **Select senders** to delete emails from  
- 🔑 **Keyword filter** for subject/body (optional)  
- 📅 **Date-based filtering**:
  - Delete emails older than X days
  - Delete emails within a custom **date range**
- 📊 **Progress bars** for both scanning & deletion
- 🔐 Uses **OAuth 2.0** with `credentials.json`
- ⚡ Fast metadata retrieval using **batch requests**
- 💻 Clean and responsive **Tkinter GUI**

---

## 🚀 Getting Started

### 1. Clone this Repository

```bash
git clone https://github.com/yourusername/gmail-inbox-cleaner.git
cd gmail-inbox-cleaner
```

### 2. Install Requirements

```bash
pip install -r requirements.txt
```

Required Python packages:
- `google-api-python-client`
- `google-auth`
- `google-auth-oauthlib`

### 3. Setup Gmail API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the **Gmail API**
3. Create **OAuth 2.0 client credentials** (type: Desktop)
4. Download `credentials.json` and place it in the root folder

> On first run, the tool will generate `token.json` automatically.

---

## ✅ Usage

```bash
python gui.py
```

Then simply:
1. Click “Scan” to fetch top N senders
2. Select senders to delete emails from
3. Optionally enter keywords, date filters, or age
4. Click “Delete” to clean your inbox 🎯

---

## ⚠️ Disclaimer

- This tool **permanently deletes emails** from your Gmail inbox.
- Use with caution. We are not responsible for data loss.

---

## 📄 License

MIT License — use, modify, and share freely.

---

## 🤝 Contributions

Contributions, bug reports, or feature requests are welcome!  
Feel free to open issues or pull requests.

---

## 👨‍💻 Author

**Santpal Singh Kalra**  
Built to simplify inbox management.

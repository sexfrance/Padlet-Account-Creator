<div align="center">
  <h2 align="center">Padlet Account Creator</h2>
  <p align="center">
    An automated tool for creating Padlet accounts with email verification support, proxy handling, and multi-threading capabilities.
    <br />
    <br />
    <a href="https://discord.cyberious.xyz">💬 Discord</a>
    ·
    <a href="#-changelog">📜 ChangeLog</a>
    ·
    <a href="https://github.com/sexfrance/Padlet-Account-Creator/issues">⚠️ Report Bug</a>
    ·
    <a href="https://github.com/sexfrance/Padlet-Account-Creator/issues">💡 Request Feature</a>
  </p>
</div>

---

### ⚙️ Installation

- Requires: `Python 3.7+`
- Make a python virtual environment: `python3 -m venv venv`
- Source the environment: `venv\Scripts\activate` (Windows) / `source venv/bin/activate` (macOS, Linux)
- Install the requirements: `pip install -r requirements.txt`

---

### 🔥 Features

- Automated Padlet account creation
- Email verification support using temporary email service
- Proxy support for avoiding rate limits
- Multi-threaded account generation
- Real-time creation tracking
- Configurable thread count
- Debug mode for troubleshooting
- Proxy/Proxyless mode support
- Automatic CSRF token handling
- Custom password support

---

### 📝 Usage

1. **Configuration**:
   Edit `input/config.toml`:

   ```toml
   [data]
   password = "optional_custom_password" # Leave empty for random password generation

   [dev]
   Debug = false
   Proxyless = false
   Threads = 1
   ```

2. **Proxy Setup** (Optional):

   - Add proxies to `input/proxies.txt` (one per line)
   - Format: `ip:port` or `user:pass@ip:port`

3. **Running the script**:

   ```bash
   python main.py
   ```

4. **Output**:
   - Created accounts are saved to `output/accounts.txt`
   - Format: `email:password`

---

### 📹 Preview

![Preview](https://i.imgur.com/oa9mtvs.gif)

---

### ❗ Disclaimers

- This project is for educational purposes only
- The author is not responsible for any misuse of this tool
- Use responsibly and in accordance with Padlet's terms of service

---

### 📜 ChangeLog

```diff
v0.0.1 ⋮ 12/26/2024
! Initial release.
```

<p align="center">
  <img src="https://img.shields.io/github/license/sexfrance/Padlet-Account-Creator.svg?style=for-the-badge&labelColor=black&color=f429ff&logo=IOTA"/>
  <img src="https://img.shields.io/github/stars/sexfrance/Padlet-Account-Creator.svg?style=for-the-badge&labelColor=black&color=f429ff&logo=IOTA"/>
  <img src="https://img.shields.io/github/languages/top/sexfrance/Padlet-Account-Creator.svg?style=for-the-badge&labelColor=black&color=f429ff&logo=python"/>
</p>

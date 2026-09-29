# Eleven ID — الون آیدی

> Telegram Username Finder & Checker built with Python and Telethon.

## 🇬🇧 English

Eleven ID is a lightweight Telegram username discovery and availability checker built with Python and Telethon.

It uses an authenticated Telegram session to check candidate usernames through Telegram's API. No browser automation or Telegram bot token is required.

### Features

- 🔐 Login with a Telegram account and persistent session
- 🔎 Check curated Telegram username candidates
- ✅ Save available usernames to `available.txt`
- 📝 Track checked usernames in `tested.txt`
- ⏳ Handles Telegram FloodWait responses automatically
- 🛡️ Keeps API credentials and session files out of Git
- 🪟 Simple Windows PowerShell / CMD setup

### Requirements

- Windows 10/11
- Python 3.11+
- A Telegram account
- Telegram API ID and API Hash from `my.telegram.org`

### Quick Start — PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
.\.venv\Scripts\python.exe main.py
```

### Easy Install

After downloading the repository:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

Or run:

```text
run.bat
```

### Environment

Create `.env` from `.env.example`:

```env
API_ID=12345678
API_HASH=your_api_hash_here
PHONE=+989xxxxxxxxxx
```

Do **not** publish `.env` or any `.session` file.

### Output

- `available.txt` — usernames reported as available by Telegram
- `tested.txt` — usernames already checked, so repeated runs can skip them

### Authentication

Eleven ID intentionally uses authenticated Telegram access. There is no anonymous / "No Login" mode in this project.

On the first run, Telethon may ask for your Telegram login code and, if enabled, your two-step verification password. After successful login, the local session can be reused.

### ⚠️ Notes

Username availability can change at any time. A username reported as available is not a permanent reservation; it must still be claimed through Telegram before someone else takes it.

Use the tool responsibly and respect Telegram's limits. FloodWait responses are handled by waiting for the duration requested by Telegram.

---

## 🇮🇷 فارسی

**الون آیدی (Eleven ID)** یک ابزار سبک برای پیدا کردن و بررسی نام‌های کاربری تلگرام است که با **Python** و **Telethon** ساخته شده است.

این برنامه با استفاده از حساب کاربری تلگرام و Session احراز هویت‌شده، نام‌های کاربری موردنظر را مستقیماً از طریق API تلگرام بررسی می‌کند.

### امکانات

- 🔐 ورود با حساب تلگرام و ذخیره Session
- 🔎 بررسی لیست نام‌های کاربری پیشنهادی
- ✅ ذخیره نام‌های کاربری آزاد در `available.txt`
- 📝 ذخیره نام‌های بررسی‌شده در `tested.txt`
- ⏳ مدیریت خودکار محدودیت FloodWait تلگرام
- 🛡️ خارج نگه‌داشتن اطلاعات حساس از GitHub
- 🪟 نصب و اجرای ساده در Windows

### پیش‌نیازها

- Windows 10/11
- Python 3.11 یا بالاتر
- حساب تلگرام
- API ID و API Hash از `my.telegram.org`

### نصب سریع

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
.\.venv\Scripts\python.exe main.py
```

یا از نصب‌کننده استفاده کنید:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

### نکات امنیتی

فایل `.env` و فایل‌های Session را هرگز در GitHub منتشر نکنید. این فایل‌ها در `.gitignore` قرار گرفته‌اند.

### احراز هویت

در نسخه نهایی Eleven ID، حالت **No Login** وجود ندارد و برنامه فقط از Login/Session تلگرام استفاده می‌کند.

در اولین اجرا ممکن است تلگرام کد ورود و در صورت فعال بودن، رمز Two-Step Verification را درخواست کند. پس از ورود موفق، Session محلی برای اجراهای بعدی استفاده می‌شود.

### خروجی‌ها

- `available.txt` — نام‌های کاربری‌ای که تلگرام آن‌ها را قابل استفاده گزارش کرده است.
- `tested.txt` — نام‌های کاربری بررسی‌شده برای جلوگیری از بررسی تکراری.

### توجه

آزاد بودن یک Username دائمی نیست و ممکن است قبل از Claim شدن توسط شخص دیگری گرفته شود. همچنین محدودیت‌های تلگرام باید رعایت شوند؛ برنامه در صورت دریافت FloodWait، مدت زمان اعلام‌شده توسط تلگرام را رعایت می‌کند.

## License

This project is provided for educational and personal use.

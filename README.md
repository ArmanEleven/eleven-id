# Eleven ID

**A Telegram username discovery tool built with Python and Telethon.**

Eleven ID checks candidate Telegram usernames through an authenticated Telegram session and writes results to local text files. Availability is a point-in-time result; it does not reserve a username.

## Features

- Authenticated Telegram session with local session reuse.
- Candidate username checking through Telegram's API.
- Results saved to `available.txt` and checked names tracked in `tested.txt`.
- Handling for Telegram `FloodWait` responses.
- Local configuration through `.env`.

## Requirements

- Windows 10 or 11
- Python 3.11+
- A Telegram account
- API credentials from [my.telegram.org/apps](https://my.telegram.org/apps)

## Install and run

Open PowerShell in the project directory:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
.\.venv\Scripts\python.exe main.py
```

Set the values in `.env`:

```dotenv
API_ID=your_api_id
API_HASH=your_api_hash
PHONE=+989xxxxxxxxxx
```

On the first run, Telegram may request a login code and, if enabled, your two-step verification password.

## One-command online setup

Download and inspect the bootstrap script before running it:

```powershell
Invoke-WebRequest "https://raw.githubusercontent.com/ArmanEleven/eleven-id/main/bootstrap.ps1" -OutFile ".\eleven-id-bootstrap.ps1"
Get-Content .\eleven-id-bootstrap.ps1
powershell -ExecutionPolicy Bypass -File .\eleven-id-bootstrap.ps1
```

The bootstrap downloads the source archive from GitHub, extracts it locally, and starts the project's installer. It requires an internet connection and a local Python installation. Always inspect scripts before running them.

## Local files

| File | Purpose |
| --- | --- |
| `available.txt` | Usernames reported as available |
| `tested.txt` | Usernames already checked |
| `.env` | Telegram API credentials and phone number |
| `telegram_finder.session` | Local Telegram login session |

## Security

- Never commit `.env` or Telegram session files.
- Treat the API hash and session file as sensitive credentials.
- Respect Telegram's rate limits and terms.
- A username may be claimed after it has been checked.

## License

Eleven ID is licensed under the MIT License. See [LICENSE](LICENSE).

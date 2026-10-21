# Eleven ID

**A Telegram username discovery tool built with Python and Telethon.**

Eleven ID checks candidate usernames through an authenticated Telegram session and writes results to local text files. It is designed for Windows and uses Telegram's API rather than browser automation.

## Features

- Sign in with a Telegram account and reuse a local session.
- Generate candidate usernames using configurable character rules.
- Save usernames reported as available to `available.txt`.
- Track checked usernames in `tested.txt`.
- Handle Telegram `FloodWait` responses.
- Configure credentials through a local `.env` file.

Availability is only a point-in-time result; it does not reserve a username.

## Requirements

- Windows 10 or 11
- Python 3.11+
- A Telegram account
- API credentials from [my.telegram.org/apps](https://my.telegram.org/apps)

## Quick start

Clone or download the repository, open PowerShell in the project directory, and run:

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

On the first run, Telegram may ask for a login code and, if enabled, your two-step verification password.

## Windows installer

The included `install.ps1` creates a virtual environment, installs dependencies, asks for the Telegram API values and phone number, writes `.env`, and starts the program.

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

### Download-and-run bootstrap

After `bootstrap.ps1` is merged into the default branch, you can download it first and inspect it before running:

```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/ArmanEleven/eleven-id/main/bootstrap.ps1" -OutFile ".\eleven-id-bootstrap.ps1"
Get-Content .\eleven-id-bootstrap.ps1
powershell -ExecutionPolicy Bypass -File .\eleven-id-bootstrap.ps1
```

The bootstrap downloads the repository archive from GitHub, extracts it to a local folder, and starts the included installer. Review scripts before executing them. The bootstrap requires an internet connection and a local Python installation.

## Output and local data

| Path | Purpose |
| --- | --- |
| `available.txt` | Usernames reported as available |
| `tested.txt` | Usernames already checked |
| `telegram_finder.session` | Local Telegram login session |
| `.env` | Local API credentials and phone number |

## Security

- Never commit `.env` or Telegram session files.
- Treat the API hash and session file as sensitive credentials.
- Use conservative request rates and follow Telegram's terms and rate limits.
- Do not assume that a username remains available after it has been checked.

## License

See the repository's license file for the applicable terms.

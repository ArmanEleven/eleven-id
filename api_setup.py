from __future__ import annotations

import re
import time
from pathlib import Path


class TelegramCoreSetupError(RuntimeError):
    pass


APPS_URL = "https://my.telegram.org/apps"


def _extract_credentials(text: str) -> tuple[int, str] | None:
    """Extract api_id/api_hash from rendered HTML/text using several patterns."""
    # API hash is 32 hex characters. Keep extraction deliberately strict.
    hash_patterns = [
        r"(?:api[_ -]?hash|app[_ -]?hash)\"?\s*[:=]\s*\"?([0-9a-fA-F]{32})",
        r"(?:api[_ -]?hash|app[_ -]?hash)[^0-9a-fA-F]{0,80}([0-9a-fA-F]{32})",
    ]
    id_patterns = [
        r"(?:api[_ -]?id|app[_ -]?id)\"?\s*[:=]\s*\"?(\d{4,})",
        r"(?:api[_ -]?id|app[_ -]?id)[^0-9]{0,80}(\d{4,})",
    ]
    api_hash = None
    api_id = None
    for pattern in hash_patterns:
        m = re.search(pattern, text, re.I)
        if m:
            api_hash = m.group(1)
            break
    for pattern in id_patterns:
        m = re.search(pattern, text, re.I)
        if m:
            api_id = m.group(1)
            break
    if api_id and api_hash:
        return int(api_id), api_hash.lower()
    return None


def _extract_from_driver(driver) -> tuple[int, str] | None:
    html = driver.page_source or ""
    found = _extract_credentials(html)
    if found:
        return found

    # Read actual DOM values/text too; this covers inputs and dynamically rendered pages.
    try:
        elements = driver.find_elements("css selector", "input, span, code, pre, div")
    except Exception:
        elements = []
    chunks = [html]
    for el in elements:
        try:
            for attr in ("value", "data-api-id", "data-api-hash", "id", "name"):
                value = el.get_attribute(attr)
                if value:
                    chunks.append(value)
            if el.text:
                chunks.append(el.text)
        except Exception:
            continue
    return _extract_credentials("\n".join(chunks))


def _save_env(path: Path, api_id: int, api_hash: str, phone: str) -> None:
    path.write_text(
        f"API_ID={api_id}\nAPI_HASH={api_hash}\nPHONE={phone}\n",
        encoding="utf-8",
    )


def setup_api_in_browser(phone: str, env_path: Path) -> tuple[int, str]:
    """Use a real Chrome session for my.telegram.org.

    This intentionally avoids the old direct HTTP login flow, which is brittle
    because Telegram can change its web authentication endpoints and tokens.
    The user completes Telegram's own login/2FA/app-creation UI; the program
    reads the resulting API credentials locally from the Apps page.
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
    except ImportError as exc:
        raise TelegramCoreSetupError(
            "Selenium is missing. Run setup.bat again or install requirements.txt."
        ) from exc

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")

    try:
        driver = webdriver.Chrome(options=options)
    except Exception as exc:
        raise TelegramCoreSetupError(
            "Chrome could not be started. Install Google Chrome and run the program again."
        ) from exc

    try:
        driver.get(APPS_URL)
        print()
        print("Telegram API setup")
        print("=" * 60)
        print("A Chrome window has been opened.")
        print("1. Log in to my.telegram.org using your Telegram account.")
        print("2. Complete the Telegram code / 2-Step Verification if requested.")
        print("3. Open 'API development tools'.")
        print("4. If no application exists, create one (any title/short name is fine).")
        print("5. Leave the page showing API ID and API Hash.")
        print("6. Return here and press Enter.")
        print()
        input("Press Enter when API ID and API Hash are visible... ")

        # Give the page a moment to finish rendering.
        for _ in range(5):
            found = _extract_from_driver(driver)
            if found:
                api_id, api_hash = found
                _save_env(env_path, api_id, api_hash, phone)
                return api_id, api_hash
            time.sleep(0.5)

        raise TelegramCoreSetupError(
            "API ID/API Hash were not found on the current page. "
            "Make sure the API development tools page is open and both values are visible."
        )
    finally:
        driver.quit()


def get_or_create_api(phone: str, env_path: Path) -> tuple[int, str]:
    """Compatibility entry point used by main.py."""
    return setup_api_in_browser(phone, env_path)


def save_env(path: Path, api_id: int, api_hash: str, phone: str) -> None:
    _save_env(path, api_id, api_hash, phone)

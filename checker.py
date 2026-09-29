from __future__ import annotations

import asyncio
import getpass
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

import aiohttp

try:
    from telethon import TelegramClient, functions
    from telethon.errors import (
        FloodWaitError,
        PhoneCodeExpiredError,
        PhoneCodeInvalidError,
        PhoneNumberInvalidError,
        PhonePasswordFloodError,
        PasswordHashInvalidError,
        RPCError,
        SessionPasswordNeededError,
    )
except ImportError:
    TelegramClient = None
    functions = None
    FloodWaitError = RPCError = PhonePasswordFloodError = Exception
    PhoneCodeExpiredError = PhoneCodeInvalidError = PhoneNumberInvalidError = Exception
    PasswordHashInvalidError = SessionPasswordNeededError = Exception


class Status(str, Enum):
    AVAILABLE = "AVAILABLE"
    LIKELY_AVAILABLE = "LIKELY AVAILABLE"
    TAKEN = "TAKEN"
    FRAGMENT = "FRAGMENT"
    UNKNOWN = "UNKNOWN"


@dataclass
class CheckResult:
    username: str
    status: Status
    detail: str = ""

    @property
    def display(self) -> str:
        return {
            Status.AVAILABLE: "OK AVAILABLE",
            Status.LIKELY_AVAILABLE: "OK LIKELY AVAILABLE",
            Status.TAKEN: "TAKEN",
            Status.FRAGMENT: "FRAGMENT",
            Status.UNKNOWN: "UNKNOWN",
        }[self.status]


def valid_username(username: str) -> bool:
    return (
        5 <= len(username) <= 32
        and username[0].isalpha()
        and username[-1].isalnum()
        and all(c.isascii() and (c.isalnum() or c == "_") for c in username)
    )


class LoginChecker:
    def __init__(self, api_id: int, api_hash: str, phone: str, session_path: Path):
        if TelegramClient is None:
            raise RuntimeError("Telethon is not installed. Run setup.bat first.")
        self.client = TelegramClient(str(session_path), api_id, api_hash)
        self.phone = phone

    async def start(self) -> None:
        # Use Telethon's standard authentication flow. It handles Telegram's
        # SRP-based 2FA protocol internally; do not manually hash the password.
        await self.client.connect()
        try:
            if await self.client.is_user_authorized():
                me = await self.client.get_me()
                print(f"Already logged in as @{me.username or 'no_username'}")
                return

            print()
            print("Telegram is sending a login code...")

            code = None
            async def ensure_code() -> str:
                nonlocal code
                if code is None:
                    code = input("Enter Telegram login code: ").strip()
                return code

            def code_callback() -> str:
                return input("Enter Telegram login code: ").strip()

            def password_callback() -> str:
                # getpass avoids echoing the 2FA password in PowerShell.
                return getpass.getpass("2-Step Verification password: ")

            try:
                await self.client.start(
                    phone=self.phone,
                    code_callback=code_callback,
                    password=password_callback,
                    max_attempts=3,
                )
            except PhonePasswordFloodError as exc:
                raise RuntimeError(
                    "Telegram temporarily blocked new login attempts for this phone "
                    "because there were too many recent attempts. Wait until Telegram "
                    "allows another login attempt, then run the program again."
                ) from exc
            except PhoneNumberInvalidError as exc:
                raise RuntimeError(
                    "Telegram rejected the phone number. Check the international format."
                ) from exc
            except PasswordHashInvalidError as exc:
                raise RuntimeError(
                    "Telegram rejected the 2-Step Verification password. "
                    "Make sure this is the cloud 2-Step password for the same Telegram account, "
                    "not the Telegram app lock/passcode."
                ) from exc
            except PhoneCodeInvalidError as exc:
                raise RuntimeError("Telegram rejected the login code.") from exc
            except PhoneCodeExpiredError as exc:
                raise RuntimeError("The Telegram login code expired. Run the program again.") from exc

            if not await self.client.is_user_authorized():
                raise RuntimeError("Telegram login did not complete.")

            me = await self.client.get_me()
            print(f"Logged in successfully as @{me.username or 'no_username'}")
        except Exception:
            if self.client.is_connected():
                await self.client.disconnect()
            raise

    async def check(self, username: str) -> CheckResult:
        if not valid_username(username):
            return CheckResult(username, Status.UNKNOWN, "Invalid username")
        try:
            await asyncio.sleep(0.20)
            await self.client(functions.account.CheckUsernameRequest(username=username))
            return CheckResult(username, Status.AVAILABLE)
        except FloodWaitError as exc:
            print(f"Flood wait: Telegram asked us to wait {exc.seconds} seconds.")
            await asyncio.sleep(exc.seconds)
            return await self.check(username)
        except RPCError as exc:
            name = type(exc).__name__
            if name == "UsernameOccupiedError":
                return CheckResult(username, Status.TAKEN)
            if name == "UsernamePurchaseAvailableError":
                return CheckResult(username, Status.FRAGMENT)
            if name == "UsernameInvalidError":
                return CheckResult(username, Status.UNKNOWN, name)
            return CheckResult(username, Status.UNKNOWN, name)
        except Exception as exc:
            return CheckResult(username, Status.UNKNOWN, type(exc).__name__)

    async def close(self) -> None:
        if self.client.is_connected():
            await self.client.disconnect()


class NoLoginChecker:
    def __init__(self) -> None:
        self.session: Optional[aiohttp.ClientSession] = None

    async def start(self) -> None:
        if self.session is None:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10),
                headers={"User-Agent": "TelegramUsernameFinder/1.0"},
            )

    async def check(self, username: str) -> CheckResult:
        if not valid_username(username):
            return CheckResult(username, Status.UNKNOWN, "Invalid username")
        await self.start()
        try:
            async with self.session.get(f"https://t.me/{username}", allow_redirects=True) as response:
                text = (await response.text(errors="ignore")).lower()
                if response.status == 200 and any(m in text for m in ("tgme_page_title", "tgme_page_extra", "tgme_action_web")):
                    return CheckResult(username, Status.TAKEN, "t.me resolved")
                if response.status in {404, 410}:
                    fragment = await self._check_fragment(username)
                    return fragment or CheckResult(username, Status.LIKELY_AVAILABLE, "No public t.me page")
                fragment = await self._check_fragment(username)
                return fragment or CheckResult(username, Status.UNKNOWN, "Could not verify publicly")
        except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
            return CheckResult(username, Status.UNKNOWN, type(exc).__name__)

    async def _check_fragment(self, username: str) -> Optional[CheckResult]:
        try:
            async with self.session.get(f"https://fragment.com/username/{username}", allow_redirects=True) as response:
                text = (await response.text(errors="ignore")).lower()
                if response.status == 200 and username.lower() in text and any(
                    marker in text for marker in ("collectible", "place a bid", "buy username", "make an offer", "current bid")
                ):
                    return CheckResult(username, Status.FRAGMENT, "Fragment collectible signal")
        except (aiohttp.ClientError, asyncio.TimeoutError):
            pass
        return None

    async def close(self) -> None:
        if self.session:
            await self.session.close()
            self.session = None

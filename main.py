import asyncio
import os
import random
import string
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient, functions
from telethon.errors import FloodWaitError, RPCError


# =========================================================
# SETTINGS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

API_ID_RAW = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
PHONE = os.getenv("PHONE")

if not API_ID_RAW or not API_HASH or not PHONE:
    raise RuntimeError(
        "Missing API_ID, API_HASH, or PHONE. Copy .env.example to .env and fill it in."
    )

try:
    API_ID = int(API_ID_RAW)
except ValueError as exc:
    raise RuntimeError("API_ID must be a number.") from exc

SESSION = str(BASE_DIR / "telegram_finder")

RESULTS = BASE_DIR / "available.txt"
TESTED = BASE_DIR / "tested.txt"

MIN_USERNAME_LENGTH = 5
MAX_USERNAME_LENGTH = 32
MAX_GENERATION_ATTEMPTS = 1_000_000


# =========================================================
# USER INPUT
# =========================================================

def ask_choice(prompt, choices):
    while True:
        value = input(prompt).strip()
        if value in choices:
            return value
        print(f"Invalid choice. Choose one of: {', '.join(choices)}")


def ask_int(prompt, minimum, maximum=None):
    while True:
        try:
            value = int(input(prompt).strip())
        except ValueError:
            print("Please enter a valid number.")
            continue

        if value < minimum:
            print(f"Value must be at least {minimum}.")
            continue

        if maximum is not None and value > maximum:
            print(f"Value must be at most {maximum}.")
            continue

        return value


def get_generator_settings():
    print()
    print("=" * 55)
    print(" USERNAME GENERATOR")
    print("=" * 55)
    print()
    print("Allowed characters:")
    print("1. English letters")
    print("2. English letters + numbers")
    print("3. English letters + _")
    print("4. English letters + numbers + _")
    print()

    character_mode = ask_choice("Select [1-4]: ", {"1", "2", "3", "4"})

    character_sets = {
        "1": string.ascii_lowercase,
        "2": string.ascii_lowercase + string.digits,
        "3": string.ascii_lowercase + "_",
        "4": string.ascii_lowercase + string.digits + "_",
    }

    allowed_chars = character_sets[character_mode]

    required = input(
        "\nLetters/text that must appear in the username (Enter = none): "
    ).strip().lower()

    if required and any(char not in allowed_chars for char in required):
        raise ValueError(
            "The required text contains characters that are not allowed "
            "by your selected character mode."
        )

    if required and required[0] not in string.ascii_lowercase:
        raise ValueError(
            "The required text must start with an English letter because "
            "Telegram usernames must start with a letter."
        )

    if len(required) > MAX_USERNAME_LENGTH:
        raise ValueError(
            f"Required text cannot be longer than {MAX_USERNAME_LENGTH} characters."
        )

    min_length = ask_int(
        f"Minimum length [{MIN_USERNAME_LENGTH}-{MAX_USERNAME_LENGTH}]: ",
        MIN_USERNAME_LENGTH,
        MAX_USERNAME_LENGTH,
    )

    max_length = ask_int(
        f"Maximum length [{min_length}-{MAX_USERNAME_LENGTH}]: ",
        min_length,
        MAX_USERNAME_LENGTH,
    )

    if len(required) > max_length:
        raise ValueError(
            "Required text is longer than the selected maximum username length."
        )

    attempts = ask_int(
        "\nHow many usernames should be checked? ",
        1,
        MAX_GENERATION_ATTEMPTS,
    )

    return {
        "allowed_chars": allowed_chars,
        "required": required,
        "min_length": min_length,
        "max_length": max_length,
        "attempts": attempts,
    }


def generate_username(settings):
    allowed_chars = settings["allowed_chars"]
    required = settings["required"]
    min_length = settings["min_length"]
    max_length = settings["max_length"]

    length = random.randint(min_length, max_length)

    if not required:
        username = random.choice(string.ascii_lowercase)
        if length > 1:
            username += "".join(
                random.choice(allowed_chars)
                for _ in range(length - 1)
            )
        return username

    if len(required) == length:
        return required

    prefix_length = random.randint(0, length - len(required))
    suffix_length = length - len(required) - prefix_length

    prefix = "".join(
        random.choice(string.ascii_lowercase)
        for _ in range(prefix_length)
    )
    suffix = "".join(
        random.choice(allowed_chars)
        for _ in range(suffix_length)
    )

    return prefix + required + suffix


def build_candidates(settings, blocked=None):
    candidates = []
    seen = set(blocked or set())

    # Leave enough room for duplicates/rejected candidates while generating.
    max_generation_rounds = max(settings["attempts"] * 10, 1000)

    for _ in range(max_generation_rounds):
        username = generate_username(settings)

        if not (MIN_USERNAME_LENGTH <= len(username) <= MAX_USERNAME_LENGTH):
            continue

        if username[0] not in string.ascii_lowercase:
            continue

        if settings["required"] and settings["required"] not in username:
            continue

        if username in seen:
            continue

        seen.add(username)
        candidates.append(username)

        if len(candidates) >= settings["attempts"]:
            break

    if len(candidates) < settings["attempts"]:
        raise RuntimeError(
            "Could not generate enough new unique usernames with these settings. "
            "Try a longer length range, remove the required text, or allow more characters."
        )

    return candidates


# =========================================================
# TELEGRAM CHECK
# =========================================================

async def check_username(client, username):
    while True:
        try:
            result = await client(
                functions.account.CheckUsernameRequest(
                    username=username
                )
            )
            return result

        except FloodWaitError as e:
            print(
                f"\n[FLOOD WAIT] Telegram asks us to wait "
                f"{e.seconds} seconds..."
            )
            await asyncio.sleep(e.seconds)

        except RPCError as e:
            name = e.__class__.__name__

            if name in {
                "UsernameInvalidError",
                "UsernameOccupiedError",
            }:
                return "taken"

            if name == "UsernamePurchaseAvailableError":
                return "purchase"

            print(f"\n[TELEGRAM ERROR] @{username} -> {name}")
            return "unknown"

        except Exception as e:
            print(f"\n[ERROR] @{username} -> {type(e).__name__}")
            return "unknown"


# =========================================================
# MAIN
# =========================================================

async def main():
    print()
    print("=" * 55)
    print(" TELEGRAM USERNAME FINDER")
    print("=" * 55)

    try:
        settings = get_generator_settings()
    except ValueError as e:
        print(f"\n[INPUT ERROR] {e}")
        return

    tested = set()

    if TESTED.exists():
        with open(TESTED, "r", encoding="utf-8") as f:
            tested = {
                line.strip().lower()
                for line in f
                if line.strip()
            }

    print("\nGenerating candidates...")
    try:
        candidates = build_candidates(settings, tested)
    except RuntimeError as e:
        print(f"\n[GENERATOR ERROR] {e}")
        return

    print(f"Generated {len(candidates)} new unique usernames.")
    print()

    client = TelegramClient(
        SESSION,
        API_ID,
        API_HASH
    )

    await client.start(phone=PHONE)

    me = await client.get_me()

    print(
        f"Logged in: "
        f"{me.first_name or ''} "
        f"@{me.username or 'no_username'}"
    )

    print()
    print(f"Total candidates: {len(candidates)}")
    print()

    available = []
    purchase_available = []

    for number, username in enumerate(candidates, start=1):
        print(
            f"[{number}/{len(candidates)}] "
            f"Checking @{username} ... ",
            end="",
            flush=True
        )

        result = await check_username(client, username)

        with open(TESTED, "a", encoding="utf-8") as f:
            f.write(username + "\n")

        if result is True:
            print("✅ AVAILABLE")
            available.append(username)

            with open(RESULTS, "a", encoding="utf-8") as f:
                f.write(f"@{username}\n")

        elif result == "taken":
            print("❌ TAKEN")

        elif result == "purchase":
            print("💎 PURCHASE AVAILABLE")
            purchase_available.append(username)

        else:
            print("⚠️ UNKNOWN")

        await asyncio.sleep(1)

    await client.disconnect()

    print()
    print("=" * 55)
    print(" FINISHED")
    print("=" * 55)
    print()
    print(f"Free available: {len(available)}")
    print(f"Purchase available: {len(purchase_available)}")
    print(f"Saved free usernames to: {RESULTS}")
    print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped by user.")

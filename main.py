import asyncio
import os
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


# =========================================================
# 500 CURATED USERNAMES
# =========================================================

USERNAMES = [
    # names / name-like
    "alina", "elena", "milen", "mykel", "miley",
    "elina", "nolan", "logan", "lucas", "louis",
    "milan", "miles", "riley", "rylan", "ryder",
    "riven", "raven", "river", "reina", "reese",
    "siena", "siena", "selena", "soren", "soren",
    "niven", "ninae", "nolan", "noelle", "naomi",
    "kairo", "kaiya", "kiana", "kiran", "keira",
    "karen", "karin", "livia", "livio", "lilia",
    "liana", "lydia", "mayae", "maria", "marin",
    "mario", "mariah", "dylan", "dario", "davin",
    "diana", "derek", "devin", "evanx", "evian",
    "ariah", "ariel", "arian", "avery", "alexa",
    "alexi", "amber", "amelia", "bella", "bianca",
    "brina", "celia", "clara", "claire", "cora",
    "dalia", "daria", "elise", "ellae", "emily",
    "emmae", "erica", "erinx", "freya", "grace",
    "hailey", "hazel", "helen", "irisx", "islaa",
    "jadee", "julia", "julie", "kylie", "layla",
    "leila", "lenae", "lilac", "lilia", "lucia",
    "lucie", "lunae", "lydia", "maeve", "mabel",
    "madie", "madison", "naira", "natalie", "nayae",
    "nella", "olivia", "oriana", "paige", "raina",
    "sasha", "siena", "silvia", "sonia", "stella",
    "talia", "tessa", "valen", "vera", "violet",
    "vivian", "yarae", "zarae", "zelda", "zoeaa",

    # real / meaningful words
    "lumen", "haven", "raven", "river", "ocean",
    "oasis", "flora", "fauna", "lunar", "solar",
    "novae", "orbit", "comet", "cosmo", "terra",
    "aurora", "ember", "flame", "blaze", "storm",
    "cloud", "rainy", "snowy", "sunny", "bloom",
    "dream", "dreamy", "magic", "mystic", "ethos",
    "vivid", "vital", "velvet", "silent", "silver",
    "golden", "crystal", "scarlet", "violet", "indigo",
    "azure", "coral", "ivory", "amber", "jade",
    "pearl", "opal", "ruby", "onyx", "topaz",
    "sable", "ivory", "linen", "velour", "satin",
    "urban", "royal", "regal", "noble", "elite",
    "prime", "major", "brave", "boldly", "grand",
    "rapid", "swift", "agile", "vivid", "fresh",
    "clean", "clear", "bright", "shiny", "glow",
    "shine", "spark", "flare", "light", "dawn",
    "dusk", "night", "dream", "wishy", "faith",
    "hope", "peace", "grace", "truth", "trust",
    "heart", "soul", "spirit", "angel", "heaven",
    "bliss", "smile", "happy", "lucky", "charm",
    "magic", "wonder", "beauty", "lovely", "sweet",
    "dreamer", "wander", "voyage", "travel", "roamer",
    "forest", "garden", "meadow", "island", "coast",
    "shore", "beach", "ocean", "wavey", "breeze",
    "windy", "cloudy", "sunset", "sunrise", "moonlight",
    "starlit", "stella", "cosmic", "galaxy", "venus",
    "marsx", "neptune", "saturn", "pluto", "apollo",

    # brandable
    "velin", "velia", "velar", "velor", "velis",
    "vella", "viora", "viven", "vexia", "vexor",
    "vexen", "nexia", "nexon", "nexar", "nexel",
    "nexis", "nexor", "nexen", "nivia", "nivor",
    "nivex", "novia", "novel", "novar", "novin",
    "novix", "novel", "lunia", "lunex", "lunor",
    "lunar", "lumia", "lumex", "lumor", "lumis",
    "aurea", "auren", "aurix", "auria", "avena",
    "avira", "avion", "avira", "arven", "arvin",
    "arion", "ariel", "orion", "orionx", "oriva",
    "orelia", "elora", "elara", "elvia", "elora",
    "evora", "evian", "evora", "evara", "evelin",
    "soren", "sorin", "soria", "sorel", "sorenx",
    "riven", "rivan", "rivenx", "rivia", "rivena",
    "ravin", "ravia", "ravenx", "ravel", "raven",
    "maven", "mavie", "mavin", "mavix", "mavon",
    "milan", "milano", "milea", "milen", "milon",
    "mylen", "myles", "mykel", "mykae", "myria",
    "kairo", "kairi", "kaien", "kaine", "kairox",
    "kaela", "kaeli", "kalen", "kalin", "kalix",
    "daven", "davin", "davon", "dario", "darien",
    "daren", "daria", "davin", "devin", "devon",
    "evren", "evrenx", "evora", "evian", "evira",
    "silan", "silen", "silas", "silva", "sivan",
    "siven", "sorin", "soren", "solen", "solis",
    "solia", "solar", "sonia", "sonic", "sonar",
    "talen", "talia", "talon", "tavin", "tavia",
    "torin", "toria", "tovin", "varen", "varin",
    "varia", "vance", "vanya", "vella", "velin",
    "zaren", "zaria", "ziven", "zivan", "zoria",
    "zorin", "zella", "zelia", "zelin", "ziven",

    # aesthetic / short
    "velvet", "midnight", "daydream", "moonlit",
    "starlit", "sunbeam", "moonbeam", "wildfire",
    "everly", "eternal", "endless", "infinite",
    "infinity", "timeless", "forever", "serene",
    "serenity", "elegant", "classic", "modern",
    "minimal", "simple", "secret", "hidden",
    "mystery", "shadow", "shaded", "darkly",
    "nightly", "dreamer", "dreamy", "lovely",
    "pretty", "beauty", "divine", "angelic",
    "celestial", "heavenly", "cosmic", "stellar",
    "astral", "nebula", "galaxy", "eclipse",
    "zenith", "horizon", "sunrise", "sunset",
    "twilight", "evening", "morning", "autumn",
    "winter", "spring", "summer", "breeze",
    "whisper", "echoes", "melody", "rhythm",
    "music", "sonnet", "poetic", "poetry", "verse",
    "story", "novel", "novelty", "chapter", "legend",
    "legacy", "destiny", "fortune", "wonder",
    "miracle", "blessed", "gentle", "kindly",
    "honest", "humble", "noble", "royal", "regal",
    "golden", "silver", "crimson", "scarlet", "violet",
    "indigo", "azure", "cobalt", "coral", "ivory",
    "pearl", "opal", "ruby", "amber", "jade",
    "onyx", "sapphire", "topaz", "diamond", "crystal",

    # tech / modern
    "pixel", "pixels", "cloudy", "cyber", "cyberx",
    "coder", "coding", "devon", "devin", "logic",
    "logicx", "binary", "bytey", "bytes", "cache",
    "server", "stack", "stacks", "script", "syntax",
    "debug", "debugx", "matrix", "vector", "vertex",
    "quantum", "neural", "vision", "future", "futurex",
    "digital", "modern", "techno", "robot", "robotx",
    "cypher", "cipher", "signal", "socket", "kernel",
    "memory", "module", "system", "engine", "portal",
    "online", "offline", "stream", "streamx", "pixelx",
    "nexus", "nexusr", "orbitx", "nova", "novax",
    "astro", "astral", "cosmos", "cosmic", "lunar",
    "solarx", "stella", "stellar", "zenith", "apex",
    "prime", "alpha", "omega", "sigma", "delta",
    "gamma", "theta", "lambda", "vector", "vertex",
    "matrix", "fusion", "vision", "focus", "motion",
    "action", "energy", "power", "pulse", "tempo",
    "spark", "flare", "flash", "glow", "light",
    "bright", "shine", "shiny", "blaze", "flame",
    "ember", "frost", "frosty", "storm", "thunder",
    "lightning", "rain", "rainy", "cloud", "cloudy",
    "wind", "windy", "breeze", "ocean", "river",
    "raven", "wolf", "tiger", "eagle", "falcon",
    "lion", "panther", "foxes", "viper", "cobra",
    "leopard", "jaguar", "phoenix", "dragon", "atlas",
    "apollo", "hermes", "ares", "zeus", "venus",
    "loki", "odin", "nova", "orion", "titan",
]


# =========================================================
# CLEAN + UNIQUE
# =========================================================

USERNAMES = list(dict.fromkeys(
    u.lower()
    for u in USERNAMES
    if u.isalpha() and u.isascii() and len(u) >= 5
))

print(f"Loaded {len(USERNAMES)} usernames.")


# =========================================================
# CHECK
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

            # این موارد معمولاً یعنی username قابل استفاده نیست
            if name in {
                "UsernameInvalidError",
                "UsernameOccupiedError",
            }:
                return False

            print(
                f"\n[TELEGRAM ERROR] @{username} -> {name}"
            )

            return None

        except Exception as e:

            print(
                f"\n[ERROR] @{username} -> {type(e).__name__}"
            )

            return None


# =========================================================
# MAIN
# =========================================================

async def main():

    client = TelegramClient(
        SESSION,
        API_ID,
        API_HASH
    )

    print()
    print("=" * 55)
    print(" TELEGRAM USERNAME FINDER")
    print("=" * 55)
    print()

    await client.start(phone=PHONE)

    me = await client.get_me()

    print(
        f"Logged in: "
        f"{me.first_name or ''} "
        f"@{me.username or 'no_username'}"
    )

    print()
    print(f"Total candidates: {len(USERNAMES)}")
    print()

    available = []
    tested = set()

    if TESTED.exists():

        with open(
            TESTED,
            "r",
            encoding="utf-8"
        ) as f:

            tested = {
                line.strip().lower()
                for line in f
                if line.strip()
            }

    for number, username in enumerate(
        USERNAMES,
        start=1
    ):

        if username in tested:
            continue

        print(
            f"[{number}/{len(USERNAMES)}] "
            f"Checking @{username} ... ",
            end="",
            flush=True
        )

        result = await check_username(
            client,
            username
        )

        with open(
            TESTED,
            "a",
            encoding="utf-8"
        ) as f:

            f.write(username + "\n")

        if result is True:

            print("✅ AVAILABLE")

            available.append(username)

            with open(
                RESULTS,
                "a",
                encoding="utf-8"
            ) as f:

                f.write(f"@{username}\n")

        elif result is False:

            print("❌ TAKEN")

        else:

            print("⚠️ UNKNOWN")

        # فاصله‌ی منطقی بین درخواست‌ها
        await asyncio.sleep(1)

    await client.disconnect()

    print()
    print("=" * 55)
    print(" FINISHED")
    print("=" * 55)
    print()
    print(f"Available: {len(available)}")
    print(f"Saved to: {RESULTS}")
    print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped by user.")

from __future__ import annotations

import random
import string
from dataclasses import dataclass

VOWELS = "aeiou"
CONSONANTS = "bcdfghjklmnpqrstvwxyz"

READABLE_PARTS = [
    "nova", "luma", "vexa", "nexa", "mira", "sora", "zora", "luna",
    "vela", "nora", "riva", "kira", "aero", "echo", "halo", "iris",
    "onyx", "ruby", "vibe", "wave", "glow", "star", "moon", "nova",
    "zen", "pixel", "orbit", "dream", "swift", "royal", "ember",
]


@dataclass
class GenerationConfig:
    count: int
    min_length: int
    max_length: int
    special_letters: str
    special_mode: int
    allow_underscore: bool
    allow_numbers: bool
    style: str


def _make_random(length: int, cfg: GenerationConfig) -> str:
    alphabet = string.ascii_lowercase
    if cfg.allow_numbers:
        alphabet += string.digits

    if cfg.style == "special":
        chars = []
        for i in range(length):
            pool = CONSONANTS if i % 2 == 0 else VOWELS
            chars.append(random.choice(pool))
        value = "".join(chars)
    else:
        value = "".join(random.choice(alphabet) for _ in range(length))

    if cfg.special_letters:
        letters = list(cfg.special_letters)

        if cfg.special_mode == 1:  # together
            if len(letters) <= length:
                start = random.randint(0, length - len(letters))
                value = value[:start] + "".join(letters) + value[start + len(letters):]
        elif cfg.special_mode == 2:  # separate
            positions = random.sample(range(length), min(len(letters), length))
            for pos, char in zip(positions, letters):
                value = value[:pos] + char + value[pos + 1:]
        else:  # random
            for char in letters:
                pos = random.randrange(length)
                value = value[:pos] + char + value[pos + 1:]

    if cfg.allow_underscore and random.random() < 0.20 and length >= 3:
        pos = random.randint(1, length - 2)
        value = value[:pos] + "_" + value[pos + 1:]

    return value


def generate_usernames(cfg: GenerationConfig) -> list[str]:
    if cfg.min_length < 5:
        raise ValueError("Minimum length cannot be below 5.")
    if cfg.max_length > 32:
        raise ValueError("Maximum length cannot exceed 32.")

    result: set[str] = set()
    attempts = 0
    max_attempts = max(cfg.count * 100, 10000)

    while len(result) < cfg.count and attempts < max_attempts:
        attempts += 1
        length = random.randint(cfg.min_length, cfg.max_length)
        value = _make_random(length, cfg).lower()

        if len(value) < 5 or len(value) > 32:
            continue

        if not all(c.isascii() and (c.isalpha() or c.isdigit() or c == "_") for c in value):
            continue

        if not (value[0].isalpha()):
            continue

        if not value[-1].isalnum():
            continue

        result.add(value)

    if len(result) < cfg.count:
        raise RuntimeError(
            f"Could only generate {len(result)} unique usernames. "
            f"Try a wider length range or allow numbers/underscore."
        )

    return list(result)

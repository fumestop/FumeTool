import re
import random
from typing import Union


_faces = [
    "(*^ω^)",
    "(*^.^*)",
    "owo",
    "OwO",
    "uwu",
    "UwU",
    "(*￣>￣)",
    ">w<",
    "^w^",
    "(/ =w=)/",
]

_patterns = {
    r"[lr]": "w",
    r"[LR]": "W",
    r"n([aeiou])": "ny\\1",
    r"N([aeiou])": "Ny\\1",
    r"N([AEIOU])": "NY\\1",
    "th": "d",
    "ove": "uv",
    "no": "nu",
}


def parse_cooldown(retry_after: Union[int, float]):
    retry_after = int(retry_after)

    hours, remainder = divmod(retry_after, 3600)
    minutes, seconds = divmod(remainder, 60)

    return minutes, seconds


def owo_fy(text: str):
    for pattern, repl in _patterns.items():
        text = re.sub(pattern, repl, text)

    return random.choice(_faces) + "\n" + f"```css\n{text}\n```"

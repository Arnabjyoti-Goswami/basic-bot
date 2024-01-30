import re
import unicodedata

import discord


def is_unicode_emoji(emoji_str: str):
    """
    Check if a given string is a unicode emoji
    """
    try:
        # Attempt to normalize the string, which might contain combining characters
        normalized_str = unicodedata.normalize("NFC", emoji_str)
        # Check if the string is categorized as an emoji
        return unicodedata.category(normalized_str) == "So"
    except ValueError:
        return False


def get_emoji(guild: discord.Guild, emoji_name: str) -> discord.Emoji | None | str:
    """
    Accepts the discord server and the discord emoji name string as arguments, and returns the unicode string for the emoji or the discord emoji if its a server specific emoji, or None if it doesn't exist in either of the two
    """
    # check if it's a custom guild emoji
    for emoji in guild.emojis:
        if emoji.name == emoji_name:
            return emoji

    # check if it's a built in discord emoji and return None or the unicode str for the emoji (if required to get the unicode str from the discord emoji name itself, we can use a simple lookup table cuz discord uses their own unique names for the emojis: https://github.com/sevenc-nanashi/discord-emoji/tree/main, here its not required because the message description obtained from the embed itslelf contains the emojis in their unicode form)
    if is_unicode_emoji(emoji_name):
        return emoji_name
    else:
        return None


def parse_duration(duration: str) -> int | None:
    """
    Parse a duration string and return the equivalent duration in seconds
    """
    unit_mapping = {
        "y": 365 * 24 * 60 * 60,
        "mo": 30 * 24 * 60 * 60,
        "w": 7 * 24 * 60 * 60,
        "d": 24 * 60 * 60,
        "h": 60 * 60,
        "m": 60,
        "s": 1,
    }

    total_seconds = 0
    duration_regex = re.findall(r"(\d+)([ymwdhms]+)", duration)

    for amount, unit in duration_regex:
        amount = int(amount)
        if unit in unit_mapping:
            total_seconds += amount * unit_mapping[unit]
        else:
            return None  # unknown unit encountered

    return total_seconds

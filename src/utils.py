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


def get_emoji_from_payload(
    guild: discord.Guild, emoji_payload: str, get_name: bool = False
) -> discord.Emoji | None | str:
    """
    Return the discord Emoji class object for raw emoji payload strings (e.g: <:JohnnyDawg:1202322942646812712> is the format for custom emojis that are server specific and not built-in discord) that are obtained by the bot in long strings like a message.

    Return the unicode emoji string if its not a custom emoji.

    Return None if its neither.

    get_name bool param: PartialEmoji and Emoji class can't be == operated. So if this param is True, get name from the Emoji class object after finding it, and return the name str instead of the Emoji object. For the bot to add the intial reactions, this would be False. This would be true, for the bot to compare a role's emoji specified in the embed message, with the reacted emoji by a user.
    """
    match = re.match(r"<:(.+):(\d+)>", emoji_payload)

    if match:
        name, id = match.groups()
        for emoji in guild.emojis:
            if emoji.name == name:
                if get_name:
                    return emoji.name
                return emoji

    # check if it's a built in discord emoji and return None or the unicode str for the emoji (if required to get the unicode str from the discord emoji name itself, we can use a simple lookup table cuz discord uses their own unique names for the emojis: https://github.com/sevenc-nanashi/discord-emoji/tree/main, here its not required because the message description obtained from the embed itself contains the emojis in their unicode form)
    if is_unicode_emoji(emoji_payload):
        return emoji_payload
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

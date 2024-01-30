import asyncio
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from utils import get_emoji, parse_duration

# Intents configuration
intents = discord.Intents.default()
intents.reactions = True  # enable reaction events
intents.message_content = True  # enable message events
intents.members = True  # required for on_reaction_remove so that both the message and the user can be found in the cache

# Initialize the bot with intents
bot = commands.Bot(command_prefix="!", intents=intents)

# Load environment variables
dotenv_path = os.path.join(os.path.abspath(""), ".env")
load_dotenv(dotenv_path)

# Get the bot token from the environment variables
bot.token = os.getenv("BOT_TOKEN")
if not bot.token:
    raise ValueError("BOT_TOKEN is not set in the .env file")


@bot.event
async def on_ready():
    """
    Configure the logging to be done upon initialization of the bot
    """
    # flush=True is provided for logging in the running docker container
    print(f"Logged in as {bot.user.name} ({bot.user.id})", flush=True)
    print("-----------", flush=True)


@bot.event
async def on_message(message: discord.Message):
    """
    Configure the bot's action to be taken for any possible message in the server
    """
    # Prevent the bot from responding to its own messages
    if message.author == bot.user:
        return

    await bot.process_commands(message)


@bot.command(name="self_roles")
async def self_roles(ctx: commands.Context, *, details: str):
    """
    Configure the self_roles command of the bot
    """
    # Check if the command is invoked by a bot or a user without the administrator permission
    if ctx.author.bot or not ctx.author.guild_permissions.administrator:
        return

    embed = discord.Embed(
        title="React Here to grab your Roles",
        description=details.strip(),
        color=discord.Color.blue(),
    )

    sent_message = await ctx.send(embed=embed)

    roles = details.strip().split("\n")

    for role_info in roles:
        try:
            emoji, role_name = role_info.strip().split(" ", 1)
            role_emoji = get_emoji(ctx.guild, emoji)

            if role_emoji:
                await sent_message.add_reaction(role_emoji)

        except ValueError:
            # handle cases where the input is not in the expected format
            await ctx.send(f"Invalid format for role: {role_info}")


@bot.event
async def on_reaction_add(
    reaction: discord.Reaction, user: discord.User | discord.Member
):
    """
    Configure the actions to be performed in the server according to the reactions added to the messages of the bot
    """
    # don't respond to reactions from bots
    if user.bot:
        return

    guild = reaction.message.channel.guild
    reacted_emoji = reaction.emoji

    # check if the bot's message is an embed
    if not (isinstance(reaction.message.embeds, list) and reaction.message.embeds):
        return

    embed = reaction.message.embeds[0]  # assuming there's only one embed in the message
    bot_msg = embed.title
    details = embed.description

    # only do something for added reactions to the bot's message if the bot's message contains a specific string
    if not bot_msg.lower().startswith("react"):
        return

    roles = details.split("\n")

    allowed_emojis = []

    for role_info in roles:
        try:
            emoji, role_name = role_info.strip().split(" ", 1)
            emoji = emoji.strip()
            role_name = role_name.strip()
            role_emoji = get_emoji(guild, emoji)

            allowed_emojis.append(role_emoji)

            role = discord.utils.get(guild.roles, name=role_name)

            if role_emoji == reacted_emoji and role:
                member = await guild.fetch_member(user.id)
                if member:
                    await member.add_roles(role)
                    return

        except ValueError:
            # handle cases where the input is not in the expected format
            pass

    # remove the reacted emoji if its not in the self_roles msg of the bot
    if reacted_emoji not in allowed_emojis:
        await reaction.remove(user)


@bot.event
async def on_reaction_remove(
    reaction: discord.Reaction, user: discord.User | discord.Member
):
    """
    Configure the actions to be performed in the server according to the reactions removed from the messages of the bot
    """
    # don't respond to reactions from bots
    if user.bot:
        return

    guild = reaction.message.channel.guild
    reacted_emoji = reaction.emoji
    msg_embeds = reaction.message.embeds

    # check if the bot's message is an embed
    if not (isinstance(msg_embeds, list) and msg_embeds):
        return

    embed = msg_embeds[0]  # assuming there's only one embed in the message
    bot_msg = embed.title
    details = embed.description

    # only do something for added reactions to the bot's message if the bot's message contains a specific string
    if not bot_msg.lower().startswith("react"):
        return

    roles = details.split("\n")

    for role_info in roles:
        try:
            emoji, role_name = role_info.strip().split(" ", 1)
            emoji = emoji.strip()
            role_name = role_name.strip()
            role_emoji = get_emoji(guild, emoji)

            role = discord.utils.get(guild.roles, name=role_name)

            if role_emoji == reacted_emoji and role:
                member = await guild.fetch_member(user.id)
                if member and role in member.roles:
                    await member.remove_roles(role)
                    return

        except ValueError:
            # handle cases where the input is not in the expected format
            pass


@bot.command(name="mute")
async def mute(ctx: commands.Context, member: discord.Member, duration: str = None):
    """
    Configure the mute command of the bot
    """
    # Check if the command is invoked by a bot or a user without the administrator permission
    if ctx.author.bot or not ctx.author.guild_permissions.administrator:
        return

    muted_role_name = "muted"
    muted_role = discord.utils.get(ctx.guild.roles, name=muted_role_name)

    # if the role doesn't already exist and isn't configured by the server administrators, then make a basic muted role and apply it to all the channels with only the permission of being able to send messages being off
    if not muted_role:
        muted_role = await ctx.guild.create_role(name=muted_role_name)
        for channel in ctx.guild.channels:
            if channel.type == discord.ChannelType.text:
                await channel.set_permissions(muted_role, send_messages=False)

    # add the role and remove all other roles from the mentioned member
    await member.edit(roles=[muted_role])

    # send a confirmation message
    if duration:
        await ctx.send(f"{member.mention} has been muted for {duration}")
    if not duration:
        await ctx.send(f"{member.mention} has been muted indefinitely")

    # if a duration is specified, unmute the user after the specified time if not unmuted already
    if duration:
        duration_seconds = parse_duration(duration)
        if duration_seconds is not None:
            await asyncio.sleep(duration_seconds)
            if muted_role in member.roles:
                await member.remove_roles(muted_role)


@bot.command(name="unmute")
async def unmute(ctx: commands.Context, member: discord.Member):
    """
    Configure the unmute command of the bot
    """
    # check if the command is used by a bot or a user without the administrator permission
    if ctx.author.bot or not ctx.author.guild_permissions.administrator:
        return

    muted_role_name = "muted"
    muted_role = discord.utils.get(ctx.guild.roles, name=muted_role_name)

    if muted_role:
        if muted_role in member.roles:
            await member.remove_roles(muted_role)
            await ctx.send(f"{member.mention} has been unmuted.")
        else:
            await ctx.send(f"{member.mention} is not muted.")
    else:
        await ctx.send(
            "The 'muted' role does not exist. Create it or use the 'mute' command once."
        )


@bot.command(name="reminder")
async def remind_me(ctx: commands.Context, duration: str, *, message: str):
    """
    Configure the reminder command of the bot
    """
    if not duration or not message:
        await ctx.send("Please provide a valid duration and message for the reminder.")
        return

    duration_seconds = parse_duration(duration).total_seconds()
    if not duration_seconds:
        await ctx.send(
            "Invalid duration format. Please use a valid duration format (e.g., '1h30m')."
        )
        return

    await ctx.send(f"Reminder set for {duration} from now.")

    await asyncio.sleep(duration_seconds)

    # Send the reminder message after the specified duration
    await ctx.send(f"{ctx.author.mention}, {message}")


if __name__ == "__main__":
    bot.run(bot.token)

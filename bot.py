import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio
import random

# -----------------------------
# CONFIG
# -----------------------------
REQUIRED_GUILD_ID = 1487086105479352501
SERVER_INVITE = "https://discord.gg/M2DebeaJga"

# Blacklist storage
blacklisted_users = set()

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True  # IMPORTANT: required for membership checks
bot = commands.Bot(command_prefix='!', intents=intents)


# -----------------------------
# CHECK IF USER IS IN REQUIRED SERVER
# -----------------------------
async def is_member_of_required_guild(user_id: int) -> bool:
    guild = bot.get_guild(REQUIRED_GUILD_ID)
    if guild is None:
        return False

    member = guild.get_member(user_id)
    return member is not None


# -----------------------------
# CHECK BLACKLIST
# -----------------------------
async def check_blacklist(interaction: discord.Interaction):
    if interaction.user.id in blacklisted_users:
        await interaction.response.send_message(
            "❌ You are blacklisted from using this bot.",
            ephemeral=True
        )
        return True
    return False


# -----------------------------
# BOT READY
# -----------------------------
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")


# -----------------------------
# /hello COMMAND
# -----------------------------
@bot.tree.command(name="hello", description="Say hello")
async def hello(interaction: discord.Interaction):

    # Blacklist check
    if await check_blacklist(interaction):
        return

    # BLOCK users who ARE in your server
    if await is_member_of_required_guild(interaction.user.id):
        await interaction.response.send_message(
            "❌ Commands cannot be used inside my server.",
            ephemeral=True
        )
        return

    await interaction.response.send_message("Hello!")


# -----------------------------
# /burst COMMAND
# -----------------------------
@bot.tree.command(name="burst", description="Send a custom message multiple times.")
@app_commands.describe(message="The message to send", amount="How many times to send it")
async def burst(interaction: discord.Interaction, message: str, amount: int):

    # Blacklist check
    if await check_blacklist(interaction):
        return

    # BLOCK users who ARE in your server
    if await is_member_of_required_guild(interaction.user.id):
        await interaction.response.send_message(
            "❌ Commands cannot be used inside my server.",
            ephemeral=True
        )
        return

    if amount > 20:
        await interaction.response.send_message("Maximum burst amount is 20.", ephemeral=True)
        return

    await interaction.response.send_message(
        f"Sending burst of {amount} messages!",
        ephemeral=True
    )

    for i in range(amount):
        try:
            await interaction.followup.send(message)
            await asyncio.sleep(0.3)
        except:
            await interaction.followup.send("❌ Error sending", ephemeral=True)
            return


# -----------------------------
# /spamcoinflip COMMAND
# -----------------------------
@bot.tree.command(name="spamcoinflip", description="Flip a coin to decide if the bot spams your message.")
@app_commands.describe(message="The message to send", amount="How many times to send it")
async def spamcoinflip(interaction: discord.Interaction, message: str, amount: int):

    # Blacklist check
    if await check_blacklist(interaction):
        return

    # BLOCK users who ARE in your server
    if await is_member_of_required_guild(interaction.user.id):
        await interaction.response.send_message(
            "❌ Commands cannot be used inside my server.",
            ephemeral=True
        )
        return

    if amount > 20:
        await interaction.response.send_message("Maximum spam amount is 20.", ephemeral=True)
        return

    # Flip the coin
    result = random.choice(["heads", "tails"])

    if result == "tails":
        await interaction.response.send_message(
            "🪙 Coinflip: **Tails** — No spam this time.",
            ephemeral=True
        )
        return

    # Heads → spam
    await interaction.response.send_message(
        f"🪙 Coinflip: **Heads** — Spamming {amount} messages!",
        ephemeral=True
    )

    for i in range(amount):
        try:
            await interaction.followup.send(message)
            await asyncio.sleep(0.3)
        except:
            await




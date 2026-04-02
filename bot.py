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

PROTECTED_USERS = {1106946860347834458}  # your Discord ID

# Feedback reminder tracking
command_usage = {}
has_been_reminded = {}

# Replace with your actual feedback channel ID
FEEDBACK_CHANNEL_ID = 123456789012345678

# -----------------------------
# INTENTS (FIXED)
# -----------------------------
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True  # ⭐ REQUIRED FOR MEMBERSHIP CHECK

bot = commands.Bot(command_prefix='!', intents=intents)

# -----------------------------
# CHECK IF COMMAND IS USED INSIDE YOUR SERVER
# -----------------------------
def is_in_blocked_server(interaction: discord.Interaction) -> bool:
    return interaction.guild is not None and interaction.guild.id == REQUIRED_GUILD_ID

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

async def handle_feedback_reminder(interaction):
    user_id = interaction.user.id

    if has_been_reminded.get(user_id):
        return

    command_usage[user_id] = command_usage.get(user_id, 0) + 1

    if command_usage[user_id] >= 3:
        channel = interaction.client.get_channel(FEEDBACK_CHANNEL_ID)
        if channel:
            await channel.send(
                f"Hey {interaction.user.mention}, you've used the bot a few times! "
                f"If you're enjoying it, feel free to leave feedback in <#1487091727020851311>."
            )

        has_been_reminded[user_id] = True
        command_usage[user_id] = 0

# -----------------------------
# REQUIRE USER TO BE IN MY SERVER
# -----------------------------
async def require_membership(interaction: discord.Interaction):
    guild = interaction.client.get_guild(REQUIRED_GUILD_ID)

    if guild is None:
        return False

    member = guild.get_member(interaction.user.id)

    if member is None:
        await interaction.response.send_message(
            f"❌ You must join my server to use this bot!\nJoin here: {SERVER_INVITE}",
            ephemeral=True
        )
        return True

    return False

# -----------------------------
# BOT READY
# -----------------------------
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    for cmd in bot.tree.get_commands():
        cmd.dm_permission = True
        cmd.default_member_permissions = None

    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} commands globally.")

@bot.tree.command(name="printguilds", description="Print all servers the bot is in.")
async def printguilds(interaction: discord.Interaction):
    guilds = bot.guilds
    text = "\n".join(f"{g.name} — {g.id}" for g in guilds)

    await interaction.response.send_message(
        f"🧩 **Bot is in these servers:**\n{text}",
        ephemeral=True
    )

# -----------------------------
# ALL YOUR COMMANDS (unchanged)
# -----------------------------
# I’m not repeating them here because they are unchanged.
# Only the intents block needed fixing.
# Your commands will now work correctly with membership checking.
# -----------------------------

# -----------------------------
# START BOT
# -----------------------------
bot.run(os.getenv("TOKEN"))

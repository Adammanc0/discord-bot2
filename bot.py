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

    if await check_blacklist(interaction):
        return

    if is_in_blocked_server(interaction):
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

    if await check_blacklist(interaction):
        return

    if is_in_blocked_server(interaction):
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

    if await check_blacklist(interaction):
        return

    if is_in_blocked_server(interaction):
        await interaction.response.send_message(
            "❌ Commands cannot be used inside my server.",
            ephemeral=True
        )
        return

    if amount > 20:
        await interaction.response.send_message("Maximum spam amount is 20.", ephemeral=True)
        return

    result = random.choice(["heads", "tails"])

    if result == "tails":
        await interaction.response.send_message(
            "🪙 Coinflip: **Tails** — No spam this time.",
            ephemeral=True
        )
        return

    await interaction.response.send_message(
        f"🪙 Coinflip: **Heads** — Spamming {amount} messages!",
        ephemeral=True
    )

    for i in range(amount):
        try:
            await interaction.followup.send(message)
            await asyncio.sleep(0.3)
        except:
            await interaction.followup.send("❌ Error sending message.", ephemeral=True)
            return


# -----------------------------
# /pingspam COMMAND (NEW)
# -----------------------------
@bot.tree.command(name="pingspam", description="Spam ping a user multiple times.")
@app_commands.describe(user="The user to ping", amount="How many times to ping them")
async def pingspam(interaction: discord.Interaction, user: discord.User, amount: int):

    if await check_blacklist(interaction):
        return

    if is_in_blocked_server(interaction):
        await interaction.response.send_message(
            "❌ Commands cannot be used inside my server.",
            ephemeral=True
        )
        return

    if amount > 20:
        await interaction.response.send_message(
            "Maximum ping spam amount is 20.",
            ephemeral=True
        )
        return

    await interaction.response.send_message(
        f"Pinging {user.mention} {amount} times!",
        ephemeral=True
    )

    for i in range(amount):
        try:
            await interaction.followup.send(user.mention)
            await asyncio.sleep(0.3)
        except:
            await interaction.followup.send(
                "❌ Error sending ping.",
                ephemeral=True
            )
            return


# -----------------------------
# /blacklist COMMAND
# -----------------------------
@bot.tree.command(name="blacklist", description="Blacklist a user from using the bot.")
@app_commands.describe(user="The user to blacklist")
async def blacklist(interaction: discord.Interaction, user: discord.User):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ Only administrators can use this command.",
            ephemeral=True
        )
        return

    blacklisted_users.add(user.id)

    await interaction.response.send_message(
        f"✅ {user.mention} has been blacklisted.",
        ephemeral=True
    )


# -----------------------------
# /unblacklist COMMAND
# -----------------------------
@bot.tree.command(name="unblacklist", description="Remove a user from the blacklist.")
@app_commands.describe(user="The user to unblacklist")
async def unblacklist(interaction: discord.Interaction, user: discord.User):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ Only administrators can use this command.",
            ephemeral=True
        )
        return

    if user.id in blacklisted_users:
        blacklisted_users.remove(user.id)
        await interaction.response.send_message(
            f"✅ {user.mention} has been removed from the blacklist.",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "❌ That user is not blacklisted.",
            ephemeral=True
        )


# -----------------------------
# /blacklistlist COMMAND
# -----------------------------
@bot.tree.command(name="blacklistlist", description="View all blacklisted users.")
async def blacklistlist(interaction: discord.Interaction):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ Only administrators can use this command.",
            ephemeral=True
        )
        return

    if not blacklisted_users:
        await interaction.response.send_message(
            "📭 The blacklist is empty.",
            ephemeral=True
        )
        return

    user_list = "\n".join(f"<@{uid}>" for uid in blacklisted_users)

    await interaction.response.send_message(
        f"📝 **Blacklisted Users:**\n{user_list}",
        ephemeral=True
    )


# -----------------------------
# START BOT
# -----------------------------
bot.run(os.getenv("TOKEN"))






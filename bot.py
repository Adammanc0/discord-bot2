import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio

# -----------------------------
# CONFIG
# -----------------------------
REQUIRED_GUILD_ID = 1487086105479352501
SERVER_INVITE = "https://discord.gg/bwMg2mUD"

# Blacklist storage
blacklisted_users = set()


# Helper: Check blacklist
async def check_blacklist(interaction: discord.Interaction):
    if interaction.user.id in blacklisted_users:
        await interaction.response.send_message(
            "❌ You are blacklisted from using this bot.",
            ephemeral=True
        )
        return True
    return False


intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)


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
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def hello(interaction: discord.Interaction):

    # Blacklist check
    if await check_blacklist(interaction):
        return

    # DM check
    if interaction.guild is None:
        await interaction.response.send_message(
            f"You must be in my server to use this command!\nJoin here:\n{SERVER_INVITE}",
            ephemeral=True
        )
        return

    # Wrong server check
    if interaction.guild.id != REQUIRED_GUILD_ID:
        await interaction.response.send_message(
            f"You must be in my server to use this command!\nJoin here:\n{SERVER_INVITE}",
            ephemeral=True
        )
        return

    await interaction.response.send_message("Hello!")


# -----------------------------
# /burst COMMAND
# -----------------------------
@bot.tree.command(name="burst", description="Send a custom message multiple times.")
@app_commands.describe(message="The message to send", amount="How many times to send it")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def burst(interaction: discord.Interaction, message: str, amount: int):

    # Blacklist check
    if await check_blacklist(interaction):
        return

    # DM check
    if interaction.guild is None:
        await interaction.response.send_message(
            f"You must be in my server to use this command!\nJoin here:\n{SERVER_INVITE}",
            ephemeral=True
        )
        return

    # Wrong server check
    if interaction.guild.id != REQUIRED_GUILD_ID:
        await interaction.response.send_message(
            f"You must be in my server to use this command!\nJoin here:\n{SERVER_INVITE}",
            ephemeral=True
        )
        return

    # Validate amount
    if amount > 20:
        await interaction.response.send_message(
            "Maximum burst amount is 20.",
            ephemeral=True
        )
        return

    # First message (ephemeral)
    await interaction.response.send_message(
        f"Sending burst of {amount} messages!",
        ephemeral=True
    )

    # Burst loop (public)
    for i in range(amount):
        try:
            await interaction.followup.send(message)
            await asyncio.sleep(0.3)

        except discord.Forbidden:
            await interaction.followup.send("❌ Can't send messages", ephemeral=True)
            return

        except Exception as e:
            await interaction.followup.send(f"❌ Error sending: {e}", ephemeral=True)
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




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
# /pingspam COMMAND
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
# /ghostpingspam COMMAND
# -----------------------------
@bot.tree.command(name="ghostpingspam", description="Ping a user repeatedly and delete the messages instantly.")
@app_commands.describe(user="The user to ghost ping", amount="How many times to ghost ping them")
async def ghostpingspam(interaction: discord.Interaction, user: discord.User, amount: int):

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
            "Maximum ghost ping amount is 20.",
            ephemeral=True
        )
        return

    await interaction.response.send_message(
        f"Ghost pinging {user.mention} {amount} times...",
        ephemeral=True
    )

    for i in range(amount):
        try:
            msg = await interaction.followup.send(user.mention)
            await msg.delete()
            await asyncio.sleep(0.25)
        except:
            await interaction.followup.send(
                "❌ Error ghost pinging.",
                ephemeral=True
            )
            return


# -----------------------------
# /roast COMMAND
# -----------------------------
@bot.tree.command(name="roast", description="Send a playful, harmless roast to a user.")
@app_commands.describe(user="The user to roast")
async def roast(interaction: discord.Interaction, user: discord.User):

    if await check_blacklist(interaction):
        return

    if is_in_blocked_server(interaction):
        await interaction.response.send_message(
            "❌ Commands cannot be used inside my server.",
            ephemeral=True
        )
        return

    roasts = [
        "You're not dumb, you just run on low-power mode.",
        "You're like a software update — always popping up at the worst time.",
        "You're not lazy, you're just energy efficient.",
        "You're the human version of forgetting why you walked into a room.",
        "If brains were WiFi, you'd be one bar in a basement.",
        "You're not slow, the world is just too fast.",
        "You're proof that even evolution takes breaks."
    ]

    roast_line = random.choice(roasts)

    await interaction.response.send_message(
        f"{user.mention}\n{roast_line}"
    )


# -----------------------------
# /roastspam COMMAND
# -----------------------------
@bot.tree.command(name="roastspam", description="Spams roasts at a user.")
@app_commands.describe(user="The user to roast", amount="How many times to roast them")
async def roastspam(interaction: discord.Interaction, user: discord.User, amount: int):

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
            "Maximum roast spam amount is 20.",
            ephemeral=True
        )
        return

     roasts = [
        "A glow stick has a brighter future than you. Lasts longer, too.",
        "You’re like a cloud. When you disappear, it suddenly becomes a beautiful day.",
        "Sorry, I can’t think of an insult dumb enough for you to understand.",
        "Stupidity isn’t a crime, so you’re free to go.",
        "Light travels faster than sound. It explains why you seemed smart… until I finally heard you speak.",
        " I consider you my sun. Now please get 93 million miles away from here.",
        "I would smack you, but I’m against animal abuse."
    ]

    await interaction.response.send_message(
        f"Roasting {user.mention} {amount} times...",
        ephemeral=True
    )

    for i in range(amount):
        roast_line = random.choice(roasts)
        try:
            await interaction.followup.send(f"{user.mention}\n{roast_line}")
            await asyncio.sleep(0.3)
        except:
            await interaction.followup.send(
                "❌ Error sending roast.",
                ephemeral=True
            )
            return


# -----------------------------
# /randomping COMMAND (NEW)
# -----------------------------
@bot.tree.command(name="randomping", description="Ping random users in the server.")
@app_commands.describe(amount="How many random pings to send")
async def randomping(interaction: discord.Interaction, amount: int):

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
            "Maximum random ping amount is 20.",
            ephemeral=True
        )
        return

    if interaction.guild is None:
        await interaction.response.send_message(
            "❌ This command only works in servers.",
            ephemeral=True
        )
        return

    members = [m for m in interaction.guild.members if not m.bot]

    if not members:
        await interaction.response.send_message(
            "❌ No users available to ping.",
            ephemeral=True
        )
        return

    await interaction.response.send_message(
        f"Pinging random users {amount} times...",
        ephemeral=True
    )

    for i in range(amount):
        random_user = random.choice(members)
        try:
            await interaction.followup.send(random_user.mention)
            await asyncio.sleep(0.3)
        except:
            await interaction.followup.send(
                "❌ Error sending random ping.",
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






import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio
import random

# ============================================================
# CONFIG
# ============================================================
REQUIRED_GUILD_ID = 1487086105479352501
SERVER_INVITE = "https://discord.gg/qHrpUByA"

blacklisted_users = set()
PROTECTED_USERS = {1106946860347834458}  # You
BOT_ADMINS = {1106946860347834458, 1387329189455331349}  # Add more admins here

command_usage = {}
has_been_reminded = {}

FEEDBACK_CHANNEL_ID = 123456789012345678

# ============================================================
# INTENTS
# ============================================================
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def is_in_blocked_server(interaction: discord.Interaction) -> bool:
    return interaction.guild and interaction.guild.id == REQUIRED_GUILD_ID

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

# ============================================================
# BOT READY
# ============================================================
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    for cmd in bot.tree.get_commands():
        cmd.dm_permission = True
        cmd.default_member_permissions = None

    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} commands globally.")

# ============================================================
# GENERAL COMMANDS
# ============================================================
@bot.tree.command(name="hello", description="Say hello")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def hello(interaction: discord.Interaction):

    if await check_blacklist(interaction):
        return

    if is_in_blocked_server(interaction):
        await interaction.response.send_message(
            "❌ Commands cannot be used inside my server.",
            ephemeral=True
        )
        return

    await handle_feedback_reminder(interaction)
    await interaction.response.send_message("Hello!")

# ============================================================
# SPAM COMMANDS
# ============================================================
@bot.tree.command(name="burst", description="Spam a message multiple times.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
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
        await interaction.response.send_message(
            "❌ Maximum burst amount is 20.",
            ephemeral=True
        )
        return

    await interaction.response.send_message(
        f"Sending your message {amount} times!",
        ephemeral=True
    )

    await handle_feedback_reminder(interaction)

    for _ in range(amount):
        try:
            await interaction.followup.send(message)
            await asyncio.sleep(0.3)
        except:
            await interaction.followup.send("❌ Error sending", ephemeral=True)
            return


@bot.tree.command(name="spamcoinflip", description="Flip a coin to decide if the bot spams your message.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
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
        await interaction.response.send_message(
            "❌ Maximum burst amount is 20.",
            ephemeral=True
        )
        return

    result = random.choice(["heads", "tails"])

    if result == "tails":
        await interaction.response.send_message(
            "🪙 The coin landed on **tails** — no spam this time.",
            ephemeral=True
        )
        return

    await interaction.response.send_message(
        f"🪙 Heads! Spamming `{message}` {amount} times!",
        ephemeral=True
    )

    await handle_feedback_reminder(interaction)

    for _ in range(amount):
        try:
            await interaction.followup.send(message)
            await asyncio.sleep(0.3)
        except:
            await interaction.followup.send("❌ Error sending", ephemeral=True)
            return

# ============================================================
# PING COMMANDS
# ============================================================
@bot.tree.command(name="pingspam", description="Spam ping a user multiple times.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
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

    if user.id in PROTECTED_USERS:
        await interaction.response.send_message(
            "❌ You cannot target that user.",
            ephemeral=True
        )
        return

    if amount > 20:
        await interaction.response.send_message(
            "❌ Maximum ping spam amount is 20.",
            ephemeral=True
        )
        return

    await interaction.response.send_message(
        f"Pinging {user.mention} {amount} times!",
        ephemeral=True
    )

    await handle_feedback_reminder(interaction)

    for _ in range(amount):
        try:
            await interaction.followup.send(user.mention)
            await asyncio.sleep(0.3)
        except:
            await interaction.followup.send("❌ Error sending ping.", ephemeral=True)
            return


@bot.tree.command(name="ghostpingspam", description="Ghost ping a user repeatedly.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
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

    if user.id in PROTECTED_USERS:
        await interaction.response.send_message(
            "❌ You cannot target that user.",
            ephemeral=True
        )
        return

    if amount > 20:
        await interaction.response.send_message(
            "❌ Maximum ghost ping amount is 20.",
            ephemeral=True
        )
        return

    await interaction.response.send_message(
        f"Ghost pinging {user.mention} {amount} times...",
        ephemeral=True
    )

    await handle_feedback_reminder(interaction)

    for _ in range(amount):
        try:
            msg = await interaction.followup.send(user.mention)
            await msg.delete()
            await asyncio.sleep(0.25)
        except:
            await interaction.followup.send("❌ Error ghost pinging.", ephemeral=True)
            return

# ============================================================
# ROAST COMMANDS
# ============================================================
ROASTS = [
    "A glow stick has a brighter future than you.",
    "You’re like a cloud. When you disappear, it’s a better day.",
    "I can’t think of an insult simple enough for you.",
    "Stupidity isn’t a crime, so you’re free to go.",
    "Light travels faster than sound — explains why you seemed smart at first.",
    "You’re my sun. Now get 93 million miles away.",
    "I’d smack you, but I’m against animal abuse."
]

@bot.tree.command(name="roast", description="Send a playful roast to a user.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
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

    if user.id in PROTECTED_USERS:
        await interaction.response.send_message(
            "❌ You cannot target that user.",
            ephemeral=True
        )
        return

    await interaction.response.send_message(
        f"{user.mention}\n{random.choice(ROASTS)}"
    )

    await handle_feedback_reminder(interaction)


@bot.tree.command(name="roastspam", description="Spam roasts at a user.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
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
            "❌ Maximum roast spam amount is 20.",
            ephemeral=True
        )
        return

    await interaction.response.send_message(
        f"Roasting {user.mention} {amount} times...",
        ephemeral=True
    )

    await handle_feedback_reminder(interaction)

    for _ in range(amount):
        try:
            await interaction.followup.send(f"{user.mention}\n{random.choice(ROASTS)}")
            await asyncio.sleep(0.3)
        except:
            await interaction.followup.send("❌ Error sending roast.", ephemeral=True)
            return

# ============================================================
# DM TROLL
# ============================================================
@bot.tree.command(name="dmtroll", description="Send a fake spam DM for trolling.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(user="The user to DM")
async def dmtroll(interaction: discord.Interaction, user: discord.User):

    if await check_blacklist(interaction):
        return

    if user.id in PROTECTED_USERS:
        await interaction.response.send_message(
            "❌ You cannot target that user.",
            ephemeral=True
        )
        return

    await interaction.response.send_message(
        f"😈 Sending a totally real and serious message to {user.mention}...",
        ephemeral=True
    )

    messages = [
        "HEY", "HEY YOU", "READ THIS NOW", "COME HERE BRO",
        "STOP IGNORING ME", "GET OVER HERE", "HURRY UP",
        "THIS IS IMPORTANT", "...", "you just got trolled 😂"
    ]

    try:
        for msg in messages:
            await user.send(msg)
            await asyncio.sleep(1)
    except:
        await interaction.followup.send(
            "❌ Couldn't DM that user (they probably have DMs closed).",
            ephemeral=True
        )
        return

    await handle_feedback_reminder(interaction)

# ============================================================
# HELP MENU
# ============================================================
@bot.tree.command(name="help", description="Show all bot commands and what they do.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def help_command(interaction: discord.Interaction):

    if await check_blacklist(interaction):
        return

    if is_in_blocked_server(interaction):
        await interaction.response.send_message(
            "❌ Commands cannot be used inside my server.",
            ephemeral=True
        )
        return

    await handle_feedback_reminder(interaction)

    embed = discord.Embed(
        title="📘 NexuBot Help Menu",
        description="Here are all available commands:",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="👋 General",
        value="**/hello** — Say hello\n**/help** — Show this help menu",
        inline=False
    )

    embed.add_field(
        name="💬 Messaging",
        value=(
            "**/burst** — Spam a message\n"
            "**/spamcoinflip** — Coinflip spam\n"
            "**/pingspam** — Spam ping a user\n"
            "**/ghostpingspam** — Ghost ping a user\n"
            "**/dmtroll** — Fake DM spam"
        ),
        inline=False
    )

    embed.add_field(
        name="🔥 Roasting",
        value="**/roast** — Roast a user\n**/roastspam** — Spam roasts",
        inline=False
    )

    embed.add_field(
        name="🔧 Admin Commands",
        value=(
            "**/blacklist** — Blacklist a user\n"
            "**/unblacklist** — Remove blacklist\n"
            "**/blacklistlist** — View blacklist\n"
            "**/adminadd** — Add admin\n"
            "**/adminremove** — Remove admin\n"
            "**/adminlist** — List admins"
        ),
        inline=False
    )

    embed.set_footer(text="NexuBot • Created by Adam")

    await interaction.response.send_message(embed=embed, ephemeral=True)

# ============================================================
# ADMIN COMMANDS
# ============================================================
@bot.tree.command(name="blacklist", description="Blacklist a user from using the bot.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(user="The user to blacklist")
async def blacklist(interaction: discord.Interaction, user: discord.User):

    if interaction.user.id not in BOT_ADMINS:
        await interaction.response.send_message(
            "❌ Only bot admins can use this command.",
            ephemeral=True
        )
        return

    blacklisted_users.add(user.id)

    await interaction.response.send_message(
        f"✅ {user.mention} has been blacklisted.",
        ephemeral=True
    )


@bot.tree.command(name="unblacklist", description="Remove a user from the blacklist.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(user="The user to unblacklist")
async def unblacklist(interaction: discord.Interaction, user: discord.User):

    if interaction.user.id not in BOT_ADMINS:
        await interaction.response.send_message(
            "❌ Only bot admins can use this command.",
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


@bot.tree.command(name="blacklistlist", description="View all blacklisted users.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def blacklistlist(interaction: discord.Interaction):

    if interaction.user.id not in BOT_ADMINS:
        await interaction.response.send_message(
            "❌ Only bot admins can use this command.",
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


@bot.tree.command(name="adminadd", description="Add a user as a bot admin.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(user="The user to grant admin access")
async def adminadd(interaction: discord.Interaction, user: discord.User):

    if interaction.user.id != 1106946860347834458:
        await interaction.response.send_message(
            "❌ Only the bot owner can add admins.",
            ephemeral=True
        )
        return

    BOT_ADMINS.add(user.id)

    await interaction.response.send_message(
        f"✅ {user.mention} has been added as a bot admin.",
        ephemeral=True
    )

@bot.tree.command(name="adminremove", description="Remove a user from bot admins.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(user="The user to remove from admins")
async def adminremove(interaction: discord.Interaction, user: discord.User):

    if interaction.user.id != 1106946860347834458:
        await interaction.response.send_message(
            "❌ Only the bot owner can remove admins.",
            ephemeral=True
        )
        return

    if user.id == 1106946860347834458:
        await interaction.response.send_message(
            "❌ You cannot remove yourself as the owner.",
            ephemeral=True
        )
        return

    if user.id in BOT_ADMINS:
        BOT_ADMINS.remove(user.id)
        await interaction.response.send_message(
            f"✅ {user.mention} is no longer a bot admin.",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "❌ That user is not an admin.",
            ephemeral=True
        )

@bot.tree.command(name="adminlist", description="View all bot admins.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def adminlist(interaction: discord.Interaction):

    if interaction.user.id not in BOT_ADMINS:
        await interaction.response.send_message(
            "❌ Only bot admins can view the admin list.",
            ephemeral=True
        )
        return

    if not BOT_ADMINS:
        await interaction.response.send_message(
            "📭 No admins found.",
            ephemeral=True
        )
        return

    admin_list = "\n".join(f"<@{uid}>" for uid in BOT_ADMINS)

    await interaction.response.send_message(
        f"🛠️ **Bot Admins:**\n{admin_list}",
        ephemeral=True
    )



# -----------------------------
# START BOT
# -----------------------------
bot.run(os.getenv("TOKEN"))

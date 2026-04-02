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
intents.members = True  # REQUIRED FOR MEMBERSHIP CHECK

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
async def safe_check_membership(interaction: discord.Interaction):
    # Acknowledge the interaction immediately
    if not interaction.response.is_done():
        await interaction.response.defer(ephemeral=True)

    guild = interaction.client.get_guild(REQUIRED_GUILD_ID)
    if guild is None:
        return False

    member = guild.get_member(interaction.user.id)
    if member is None:
        await interaction.followup.send(
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
    if await safe_check_membership(interaction):
        return

    guilds = bot.guilds
    text = "\n".join(f"{g.name} — {g.id}" for g in guilds)

    await interaction.followup.send(
        f"🧩 **Bot is in these servers:**\n{text}",
        ephemeral=True
    )

# -----------------------------
# /hello COMMAND
# -----------------------------
@bot.tree.command(name="hello", description="Say hello")
async def hello(interaction: discord.Interaction):

    if await safe_check_membership(interaction):
        return

    if await check_blacklist(interaction):
        return

    if is_in_blocked_server(interaction):
        await interaction.followup.send(
            "❌ Commands cannot be used inside my server.",
            ephemeral=True
        )
        return

    await handle_feedback_reminder(interaction)
    await interaction.followup.send("Hello!")

# -----------------------------
# /burst COMMAND
# -----------------------------
@bot.tree.command(
    name="burst",
    description="Spam a message multiple times.",
)
@app_commands.describe(message="The message to send", amount="How many times to send it")
async def spam(interaction: discord.Interaction, message: str, amount: int):

    if await safe_check_membership(interaction):
        return

    if await check_blacklist(interaction):
        return

    if is_in_blocked_server(interaction):
        await interaction.followup.send(
            "❌ Commands cannot be used inside my server.",
            ephemeral=True
        )
        return

    if amount > 20:
        await interaction.followup.send(
            "Maximum burst amount is 20.",
            ephemeral=True
        )
        return

    await interaction.followup.send(
        f"Sending your message {amount} times!",
        ephemeral=True
    )

    await handle_feedback_reminder(interaction)

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
@bot.tree.command(
    name="spamcoinflip",
    description="Flip a coin to decide if the bot spams your message.",
)
@app_commands.describe(
    message="The message to send",
    amount="How many times to send it"
)
async def spamcoinflip(interaction: discord.Interaction, message: str, amount: int):

    if await safe_check_membership(interaction):
        return

    if await check_blacklist(interaction):
        return

    if is_in_blocked_server(interaction):
        await interaction.followup.send(
            "❌ Commands cannot be used inside my server.",
            ephemeral=True
        )
        return

    if amount > 20:
        await interaction.followup.send(
            "Maximum burst amount is 20.",
            ephemeral=True
        )
        return

    result = random.choice(["heads", "tails"])

    if result == "tails":
        await interaction.followup.send(
            "🪙 The coin landed on **tails** — no spam this time.",
            ephemeral=True
        )
        return

    await interaction.followup.send(
        f"🪙 The coin landed on **heads** — spamming `{message}` {amount} times!",
        ephemeral=True
    )

    await handle_feedback_reminder(interaction)

    for i in range(amount):
        try:
            await interaction.followup.send(message)
            await asyncio.sleep(0.3)
        except:
            await interaction.followup.send("❌ Error sending", ephemeral=True)
            return

# -----------------------------
# /pingspam COMMAND
# -----------------------------
@bot.tree.command(
    name="pingspam",
    description="Spam ping a user multiple times.",
)
@app_commands.describe(user="The user to ping", amount="How many times to ping them")
async def pingspam(interaction: discord.Interaction, user: discord.User, amount: int):

    if await safe_check_membership(interaction):
        return

    if await check_blacklist(interaction):
        return

    if is_in_blocked_server(interaction):
        await interaction.followup.send(
            "❌ Commands cannot be used inside my server.",
            ephemeral=True
        )
        return

    if user.id in PROTECTED_USERS:
        await interaction.followup.send(
            "❌ You cannot target that user.",
            ephemeral=True
        )
        return

    if amount > 20:
        await interaction.followup.send(
            "Maximum ping spam amount is 20.",
            ephemeral=True
        )
        return

    await interaction.followup.send(
        f"Pinging {user.mention} {amount} times!",
        ephemeral=True
    )

    await handle_feedback_reminder(interaction)

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
@bot.tree.command(
    name="ghostpingspam",
    description="Ping a user repeatedly and delete the messages instantly.",
)
@app_commands.describe(user="The user to ghost ping", amount="How many times to ghost ping them")
async def ghostpingspam(interaction: discord.Interaction, user: discord.User, amount: int):

    if await safe_check_membership(interaction):
        return

    if await check_blacklist(interaction):
        return

    if is_in_blocked_server(interaction):
        await interaction.followup.send(
            "❌ Commands cannot be used inside my server.",
            ephemeral=True
        )
        return

    if amount > 20:
        await interaction.followup.send(
            "Maximum ghost ping amount is 20.",
            ephemeral=True
        )
        return

    if user.id in PROTECTED_USERS:
        await interaction.followup.send(
            "❌ You cannot target that user.",
            ephemeral=True
        )
        return

    await interaction.followup.send(
        f"Ghost pinging {user.mention} {amount} times...",
        ephemeral=True
    )

    await handle_feedback_reminder(interaction)

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
@bot.tree.command(
    name="roast",
    description="Send a playful, harmless roast to a user.",
)
@app_commands.describe(user="The user to roast")
async def roast(interaction: discord.Interaction, user: discord.User):

    if await safe_check_membership(interaction):
        return

    if await check_blacklist(interaction):
        return

    if is_in_blocked_server(interaction):
        await interaction.followup.send(
            "❌ Commands cannot be used inside my server.",
            ephemeral=True
        )
        return

    if user.id in PROTECTED_USERS:
        await interaction.followup.send(
            "❌ You cannot target that user.",
            ephemeral=True
        )
        return

    roasts = [
        "A glow stick has a brighter future than you. Lasts longer, too.",
        "You’re like a cloud. When you disappear, it suddenly becomes a beautiful day.",
        "Sorry, I can’t think of an insult dumb enough for you to understand.",
        "Stupidity isn’t a crime, so you’re free to go.",
        "Light travels faster than sound. It explains why you seemed smart… until I finally heard you speak.",
        "I consider you my sun. Now please get 93 million miles away from here.",
        "I would smack you, but I’m against animal abuse."
    ]

    roast_line = random.choice(roasts)

    await interaction.followup.send(
        f"{user.mention}\n{roast_line}"
    )

    await handle_feedback_reminder(interaction)

# -----------------------------
# /roastspam COMMAND
# -----------------------------
@bot.tree.command(
    name="roastspam",
    description="Spams roasts at a user.",
)
@app_commands.describe(user="The user to roast", amount="How many times to roast them")
async def roastspam(interaction: discord.Interaction, user: discord.User, amount: int):

    if await safe_check_membership(interaction):
        return

    if await check_blacklist(interaction):
        return

    if is_in_blocked_server(interaction):
        await interaction.followup.send(
            "❌ Commands cannot be used inside my server.",
            ephemeral=True
        )
        return

    if amount > 20:
        await interaction.followup.send(
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
        "I consider you my sun. Now please get 93 million miles away from here.",
        "I would smack you, but I’m against animal abuse."
    ]

    await interaction.followup.send(
        f"Roasting {user.mention} {amount} times...",
        ephemeral=True
    )

    await handle_feedback_reminder(interaction)

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
# /dmtroll COMMAND
# -----------------------------
@bot.tree.command(
    name="dmtroll",
    description="Send a fake spam DM (for fun trolling).",
)
@app_commands.describe(user="The user to DM")
async def dmtroll(interaction: discord.Interaction, user: discord.User):

    if await safe_check_membership(interaction):
        return

    if await check_blacklist(interaction):
        return

    if user.id in PROTECTED_USERS:
        await interaction.followup.send(
            "❌ You cannot target that user.",
            ephemeral=True
        )
        return

    await interaction.followup.send(
        f"😈 Sending a totally real and serious message to {user.mention}...",
        ephemeral=True
    )

    messages = [
        "HEY",
        "HEY YOU",
        "READ THIS NOW",
        "COME AND READ THIS BRO",
        "STOP IGNORING ME",
        "GET THE FUCK HERE",
        "HURRY UP PLEASE BRO",
        "THIS IS IMPORTANT",
        "...",
        "you just got trolled 😂"
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

# -----------------------------
# /blacklist COMMAND
# -----------------------------
@bot.tree.command(name="blacklist", description="Blacklist a user from using the bot.")
@app_commands.describe(user="The user to blacklist")
async def blacklist(interaction: discord.Interaction, user: discord.User):

    if await safe_check_membership(interaction):
        return

    if interaction.user.id != 1106946860347834458:
        await interaction.followup.send(
            "❌ Only the bot owner can use this command.",
            ephemeral=True
        )
        return

    blacklisted_users.add(user.id)

    await interaction.followup.send(
        f"✅ {user.mention} has been blacklisted.",
        ephemeral=True
    )

# -----------------------------
# /unblacklist COMMAND
# -----------------------------
@bot.tree.command(name="unblacklist", description="Remove a user from the blacklist.")
@app_commands.describe(user="The user to unblacklist")
async def unblacklist(interaction: discord.Interaction, user: discord.User):

    if await safe_check_membership(interaction):
        return

    if interaction.user.id != 1106946860347834458:
        await interaction.followup.send(
            "❌ Only the bot owner can use this command.",
            ephemeral=True
        )
        return

    if user.id in blacklisted_users:
        blacklisted_users.remove(user.id)
        await interaction.followup.send(
            f"✅ {user.mention} has been removed from the blacklist.",
            ephemeral=True
        )
    else:
        await interaction.followup.send(
            "❌ That user is not blacklisted.",
            ephemeral=True
        )

# -----------------------------
# /blacklistlist COMMAND
# -----------------------------
@bot.tree.command(name="blacklistlist", description="View all blacklisted users.")
async def blacklistlist(interaction: discord.Interaction):

    if await safe_check_membership(interaction):
        return

    if interaction.user.id != 1106946860347834458:
        await interaction.followup.send(
            "❌ Only the bot owner can use this command.",
            ephemeral=True
        )
        return

    if not blacklisted_users:
        await interaction.followup.send(
            "📭 The blacklist is empty.",
            ephemeral=True
        )
        return

    user_list = "\n".join(f"<@{uid}>" for uid in blacklisted_users)

    await interaction.followup.send(
        f"📝 **Blacklisted Users:**\n{user_list}",
        ephemeral=True
    )

# -----------------------------
# START BOT
# -----------------------------
bot.run(os.getenv("TOKEN"))

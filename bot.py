import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio
import random
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)


# ============================================================
# CONFIG
# ============================================================
REQUIRED_GUILD_ID = 1487086105479352501
SERVER_INVITE = "https://discord.gg/qHrpUByA"

blacklisted_users = set()
PROTECTED_USERS = {1106946860347834458}  # You
BOT_ADMINS = {1106946860347834458, 1387329189455331349}

command_usage = {}
has_been_reminded = {}

FEEDBACK_CHANNEL_ID = 123456789012345678
CHAOS_MODE = True


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
async def check_blacklist(interaction: discord.Interaction):
    if interaction.user.id in blacklisted_users:
        embed = discord.Embed(
            title="⛔ Access Denied",
            description="You are **blacklisted** from using NexuBot.",
            color=0xDC143C
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
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


async def require_membership(interaction: discord.Interaction):
    guild = interaction.client.get_guild(REQUIRED_GUILD_ID)

    if guild is None:
        await interaction.response.send_message(
            "❌ The bot is not connected to the main server.",
            ephemeral=True
        )
        return True

    member = guild.get_member(interaction.user.id)

    if member is None:
        await interaction.response.send_message(
            f"❌ You must join my server to use this bot!\n{SERVER_INVITE}",
            ephemeral=True
        )
        return True

    return False


# ============================================================
# BOT READY
# ============================================================
OWNER_ID = 1106946860347834458  # you
owner_user = None

@bot.event
async def on_ready():
    global owner_user

    print(f"Logged in as {bot.user}")

    # Cache owner user for DM logging
    owner_user = await bot.fetch_user(OWNER_ID)
    print("Owner user cached for logging.")

    # Enable DM permissions for all commands
    for cmd in bot.tree.get_commands():
        cmd.dm_permission = True
        cmd.default_member_permissions = None

    # Sync commands
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} commands globally.")




# ============================================================
# GENERAL COMMANDS
# ============================================================
@bot.tree.command(name="hello", description="Say hello")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def hello(interaction: discord.Interaction):

    logging.info(f"/hello used by {interaction.user}")
    await send_log_dm(f"/hello used by {interaction.user}")

    if await require_membership(interaction):
        return

    if await check_blacklist(interaction):
        return

    await handle_feedback_reminder(interaction)

    embed = discord.Embed(
        title="👋 Hello!",
        description="Hope you're having a great day.",
        color=0x00FFFF
    )
    embed.set_footer(text="NexuBot • Created by Adam")

    await interaction.response.send_message(embed=embed, ephemeral=True)


# ============================================================
# SPAM COMMANDS
# ============================================================
@bot.tree.command(name="burst", description="Spam a message multiple times 1-5.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(message="The message to send", amount="How many times to send it")
async def burst(interaction: discord.Interaction, message: str, amount: int):

    logging.info(f"/burst used by {interaction.user} | amount={amount}")
    await send_log_dm(f"/burst used by {interaction.user} | amount={amount}")

    if await require_membership(interaction):
        return

    if await check_blacklist(interaction):
        return

    if amount > 5:
        embed = discord.Embed(
            title="⚠️ Limit Exceeded",
            description="Maximum burst amount is **5**.",
            color=0xDC143C
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    embed = discord.Embed(
        title="💥 Burst Activated",
        description=f"Sending your message **{amount} times**!",
        color=0x39FF14
    )
    embed.set_footer(text="NexuBot • Created by Adam")
    await interaction.response.send_message(embed=embed, ephemeral=True)

    await handle_feedback_reminder(interaction)

    for _ in range(amount):
        try:
            await interaction.followup.send(message)
            await asyncio.sleep(0.3)
        except:
            error_embed = discord.Embed(
                title="❌ Error",
                description="There was an issue sending your burst messages.",
                color=0xDC143C
            )
            error_embed.set_footer(text="NexuBot • Created by Adam")
            await interaction.followup.send(embed=error_embed, ephemeral=True)
            return





@bot.tree.command(name="spamcoinflip", description="Flip a coin to decide if the bot spams your message 1-5.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(message="The message to send", amount="How many times to send it")
async def spamcoinflip(interaction: discord.Interaction, message: str, amount: int):

    logging.info(f"/spamcoinflip used by {interaction.user} | amount={amount}")
    await send_log_dm(f"/spamcoinflip used by {interaction.user} | amount={amount}")

    if await require_membership(interaction):
        return

    if await check_blacklist(interaction):
        return

    if amount > 5:
        embed = discord.Embed(
            title="⚠️ Limit Exceeded",
            description="Maximum spam amount is **5**.",
            color=0xDC143C
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    result = random.choice(["heads", "tails"])

    if result == "tails":
        embed = discord.Embed(
            title="🪙 Coinflip Result: Tails",
            description="No spam this time.",
            color=0x2F3136
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    embed = discord.Embed(
        title="🪙 Coinflip Result: Heads!",
        description=f"Spamming `{message}` **{amount} times**!",
        color=0x39FF14
    )
    embed.set_footer(text="NexuBot • Created by Adam")
    await interaction.response.send_message(embed=embed, ephemeral=True)

    await handle_feedback_reminder(interaction)

    for _ in range(amount):
        try:
            await interaction.followup.send(message)
            await asyncio.sleep(0.3)
        except:
            error_embed = discord.Embed(
                title="❌ Error",
                description="There was an issue sending your spam messages.",
                color=0xDC143C
            )
            error_embed.set_footer(text="NexuBot • Created by Adam")
            await interaction.followup.send(embed=error_embed, ephemeral=True)
            return

@bot.tree.command(name="embedspam", description="Spam an embed message multiple times 1-5.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(message="The message to put in the embed", amount="How many embeds to send")
async def embedspam(interaction: discord.Interaction, message: str, amount: int):

    logging.info(f"/embedspam used by {interaction.user} | amount={amount}")
    await send_log_dm(f"/embedspam used by {interaction.user} | amount={amount}")

    if await require_membership(interaction):
        return

    if await check_blacklist(interaction):
        return

    if amount > 5:
        embed = discord.Embed(
            title="⚠️ Limit Exceeded",
            description="Maximum embed spam amount is **5**.",
            color=0xDC143C
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    confirm = discord.Embed(
        title="📨 Embed Spam Activated",
        description=f"Sending your embed **{amount} times**!",
        color=0x39FF14
    )
    confirm.set_footer(text="NexuBot • Created by Adam")
    await interaction.response.send_message(embed=confirm, ephemeral=True)

    await handle_feedback_reminder(interaction)

    for i in range(amount):
        try:
            emb = discord.Embed(
                title="📨 Message Embed",
                description=message,
                color=0x00FFFF
            )
            emb.set_footer(text=f"NexuBot • Created by Adam • #{i+1}")
            await interaction.followup.send(embed=emb)
            await asyncio.sleep(0.3)
        except:
            error_embed = discord.Embed(
                title="❌ Error",
                description="There was an issue sending your embed messages.",
                color=0xDC143C
            )
            error_embed.set_footer(text="NexuBot • Created by Adam")
            await interaction.followup.send(embed=error_embed, ephemeral=True)
            return


@bot.tree.command(name="gifspam", description="Spam a GIF multiple times 1-5.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(gif_url="Direct link to the GIF", amount="How many times to send it")
async def gifspam(interaction: discord.Interaction, gif_url: str, amount: int):

    logging.info(f"/gifspam used by {interaction.user} | amount={amount}")
    await send_log_dm(f"/gifspam used by {interaction.user} | amount={amount}")

    if await require_membership(interaction):
        return

    if await check_blacklist(interaction):
        return

    if amount > 5:
        embed = discord.Embed(
            title="⚠️ Limit Exceeded",
            description="Maximum GIF spam amount is **5**.",
            color=0xDC143C
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    confirm = discord.Embed(
        title="🖼️ GIF Spam Activated",
        description=f"Sending your GIF **{amount} times**!",
        color=0x39FF14
    )
    confirm.set_footer(text="NexuBot • Created by Adam")
    await interaction.response.send_message(embed=confirm, ephemeral=True)

    await handle_feedback_reminder(interaction)

    # ⭐ THIS LOOP MUST BE INDENTED INSIDE THE FUNCTION
    for i in range(amount):
        try:
            await interaction.followup.send(gif_url)
            await asyncio.sleep(0.3)
        except:
            error_embed = discord.Embed(
                title="❌ Error",
                description="There was an issue sending your GIFs.",
                color=0xDC143C
            )
            error_embed.set_footer(text="NexuBot • Created by Adam")
            await interaction.followup.send(embed=error_embed, ephemeral=True)
            return





# ============================================================
# PING COMMANDS
# ============================================================
@bot.tree.command(name="pingspam", description="Spam ping a user multiple times 1-5.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(user="The user to ping", amount="How many times to ping them")
async def pingspam(interaction: discord.Interaction, user: discord.User, amount: int):

    logging.info(f"/pingspam used by {interaction.user} on {user} | amount={amount}")
    await send_log_dm(f"/pingspam used by {interaction.user} on {user} | amount={amount}")

    if await require_membership(interaction):
        return

    if await check_blacklist(interaction):
        return

    if user.id in PROTECTED_USERS:
        embed = discord.Embed(
            title="⛔ Protected User",
            description="You cannot target this user.",
            color=0xDC143C
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if amount > 5:
        embed = discord.Embed(
            title="⚠️ Limit Exceeded",
            description="Maximum ping spam amount is **5**.",
            color=0xDC143C
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    embed = discord.Embed(
        title="🔔 Ping Spam Activated",
        description=f"Pinging {user.mention} **{amount} times**!",
        color=0x39FF14
    )
    embed.set_footer(text="NexuBot • Created by Adam")
    await interaction.response.send_message(embed=embed, ephemeral=True)

    await handle_feedback_reminder(interaction)

    for _ in range(amount):
        try:
            await interaction.followup.send(user.mention)
            await asyncio.sleep(0.3)
        except:
            error_embed = discord.Embed(
                title="❌ Error",
                description="There was an issue sending pings.",
                color=0xDC143C
            )
            error_embed.set_footer(text="NexuBot • Created by Adam")
            await interaction.followup.send(embed=error_embed, ephemeral=True)
            return



@bot.tree.command(name="ghostpingspam", description="Ghost ping a user repeatedly 1-5.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(user="The user to ghost ping", amount="How many times to ghost ping them")
async def ghostpingspam(interaction: discord.Interaction, user: discord.User, amount: int):

    logging.info(f"/ghostpingspam used by {interaction.user} on {user} | amount={amount}")
    await send_log_dm(f"/ghostpingspam used by {interaction.user} on {user} | amount={amount}")

    if await require_membership(interaction):
        return

    if await check_blacklist(interaction):
        return

    if user.id in PROTECTED_USERS:
        embed = discord.Embed(
            title="⛔ Protected User",
            description="You cannot target this user.",
            color=0xDC143C
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if amount > 5:
        embed = discord.Embed(
            title="⚠️ Limit Exceeded",
            description="Maximum ghost ping amount is **5**.",
            color=0xDC143C
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    embed = discord.Embed(
        title="👻 Ghost Ping Spam",
        description=f"Ghost pinging {user.mention} **{amount} times**...",
        color=0x8A2BE2
    )
    embed.set_footer(text="NexuBot • Created by Adam")
    await interaction.response.send_message(embed=embed, ephemeral=True)

    await handle_feedback_reminder(interaction)

    for _ in range(amount):
        try:
            msg = await interaction.followup.send(user.mention)
            await msg.delete()
            await asyncio.sleep(0.25)
        except:
            error_embed = discord.Embed(
                title="❌ Error",
                description="There was an issue ghost pinging.",
                color=0xDC143C
            )
            error_embed.set_footer(text="NexuBot • Created by Adam")
            await interaction.followup.send(embed=error_embed, ephemeral=True)
            return


# ============================================================
# ROAST COMMANDS
# ============================================================

ROASTS = [
    "Stupidity isn’t a crime, so you’re free to go.",
    "I’d say you’re dumb as a rock, but at least a rock can hold a door open.",
    "Have you ever tried not being an idiot?",
    "Most mistakes can be corrected. You are the exception to the rule.",
    "You’re the reason this country has to put directions on shampoo bottles.",
    "Don’t be ashamed of who you are. That’s a job for your parents.",
    " I consider you my sun. Now please get 93 million miles away from here.",
    "If I wanted to hurt myself, I would simply jump from your ego to your IQ.",
]


@bot.tree.command(name="roast", description="Send a playful roast to a user.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(user="The user to roast")
async def roast(interaction: discord.Interaction, user: discord.User):

    logging.info(f"/roast used by {interaction.user} on {user}")
    await send_log_dm(f"/roast used by {interaction.user} on {user}")

    if await require_membership(interaction):
        return

    if await check_blacklist(interaction):
        return

    if user.id in PROTECTED_USERS:
        embed = discord.Embed(
            title="⛔ Protected User",
            description="You cannot roast this user.",
            color=0xDC143C
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    roast_line = random.choice(ROASTS)

    embed = discord.Embed(
        title="🔥 Roast Delivered",
        description=f"{user.mention}\n\n**{roast_line}**",
        color=0x8A2BE2
    )
    embed.set_footer(text="NexuBot • Created by Adam")

    await interaction.response.send_message(embed=embed)
    await handle_feedback_reminder(interaction)



@bot.tree.command(name="roastspam", description="Spam playful roasts at a user (1–5).")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(user="The user to roast", amount="How many times to roast them")
async def roastspam(interaction: discord.Interaction, user: discord.User, amount: int):

    logging.info(f"/roastspam used by {interaction.user} on {user} | amount={amount}")
    await send_log_dm(f"/roastspam used by {interaction.user} on {user} | amount={amount}")

    if await require_membership(interaction):
        return

    if await check_blacklist(interaction):
        return

    if amount > 5:
        embed = discord.Embed(
            title="⚠️ Limit Exceeded",
            description="Maximum roast spam amount is **5**.",
            color=0xDC143C
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if user.id in PROTECTED_USERS:
        embed = discord.Embed(
            title="⛔ Protected User",
            description="You cannot roast this user.",
            color=0xDC143C
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    embed = discord.Embed(
        title="🔥 Roast Spam Activated",
        description=f"Roasting {user.mention} **{amount} times**...",
        color=0x8A2BE2
    )
    embed.set_footer(text="NexuBot • Created by Adam")

    await interaction.response.send_message(embed=embed, ephemeral=True)
    await handle_feedback_reminder(interaction)

    for _ in range(amount):
        try:
            roast_line = random.choice(ROASTS)
            await interaction.followup.send(f"{user.mention}\n**{roast_line}**")
            await asyncio.sleep(0.3)
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Error",
                description=f"There was an issue sending roasts.\n`{e}`",
                color=0xDC143C
            )
            error_embed.set_footer(text="NexuBot • Created by Adam")
            await interaction.followup.send(embed=error_embed, ephemeral=True)
            return



# ============================================================
# Rick roll
# ============================================================
@bot.tree.command(name="rickroll", description="Send a mysterious musical message to someone.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(user="The user to rickroll")
async def rickroll(interaction: discord.Interaction, user: discord.User):

    logging.info(f"/rickroll used by {interaction.user} on {user}")
    await send_log_dm(f"/rickroll used by {interaction.user} on {user}")

    if await require_membership(interaction):
        return

    if await check_blacklist(interaction):
        return

    # 🔒 Block anyone from using it on YOU (or any protected user)
    if user.id in PROTECTED_USERS:
        embed = discord.Embed(
            title="⛔ Protected User",
            description="You cannot rickroll this user.",
            color=0xDC143C
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # ✔ Send the Rickroll line (no embed)
    await interaction.response.send_message(
        f"""{user.mention}
**You know the rules and so do I
A full commitment's what I'm thinking of
You wouldn't get this from any other guy
I just wanna tell you how I'm feeling
Gotta make you understand
Never gonna give you up {user.mention}
Never gonna let you down
Never gonna run around and desert you
Never gonna make you cry
Never gonna say goodbye
Never gonna tell a lie and hurt you
We've known each other for so long
Your heart's been aching but you're too shy to say it
Inside we both know what's been going on
We know the game and we're gonna play it
And if you ask me how I'm feeling
Don't tell me you're too blind to see
Never gonna give you up {user.mention}
Never gonna let you down
Never gonna run around and desert you
Never gonna make you cry
Never gonna say goodbye
Never gonna tell a lie and hurt you
No, I'm never gonna give you up
No, I'm never gonna let you down
No, I'll never run around and hurt you
Never, ever desert you
We've known each other for so long
Your heart's been aching but
Never gonna give you up {user.mention}
Never gonna let you down
Never gonna run around and desert you
Never gonna make you cry
Never gonna say goodbye
Never gonna tell a lie and hurt you
No, I'm never gonna give you up {user.mention}
No, I'm never gonna let you down
No, I'll never run around and hurt you
I'll never, ever desert you**"""
    )


# ============================================================
# Fake Ban
# ============================================================
@bot.tree.command(name="fakeban", description="Pretend to ban a user for fun.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(user="The user to fake-ban")
async def fakeban(interaction: discord.Interaction, user: discord.User):

    logging.info(f"/fakeban used by {interaction.user} on {user}")
    await send_log_dm(f"/fakeban used by {interaction.user} on {user}")

    # Membership check
    if await require_membership(interaction):
        return

    # Blacklist check
    if await check_blacklist(interaction):
        return

    # Protected users (like you)
    if user.id in PROTECTED_USERS:
        embed = discord.Embed(
            title="⛔ Protected User",
            description="You cannot fake-ban this user.",
            color=0xDC143C
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # ✔ Activation embed (just like burst)
    embed = discord.Embed(
        title="🔨 Fake Ban Activated",
        description=f"Pretending to ban {user.mention}...",
        color=0x8A2BE2
    )
    embed.set_footer(text="NexuBot • Created by Adam")

    await interaction.response.send_message(embed=embed, ephemeral=True)

    await handle_feedback_reminder(interaction)

    # ✔ Actual fake ban message (followup, like burst)
    try:
        await interaction.followup.send(
            f"🔨 **{user.mention} has been banned from the server.**"
        )
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Error",
            description=f"There was an issue sending the fake ban.\n`{e}`",
            color=0xDC143C
        )
        error_embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.followup.send(embed=error_embed, ephemeral=True)






import random

@bot.tree.command(name="ipgrab", description="Generate a fake IP.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(user="The user to fake-track")
async def fakeip(interaction: discord.Interaction, user: discord.User):

    logging.info(f"/fakeip used by {interaction.user} on {user}")
    await send_log_dm(f"/fakeip used by {interaction.user} on {user}")

    # Membership check
    if await require_membership(interaction):
        return

    # Blacklist check
    if await check_blacklist(interaction):
        return

    # Protected users (like you)
    if user.id in PROTECTED_USERS:
        embed = discord.Embed(
            title="⛔ Protected User",
            description="You cannot use this command on this user.",
            color=0xDC143C
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # ✔ Activation embed (like fakeban)
    embed = discord.Embed(
        title="📡 Fake Trace Activated",
        description=f"Scanning {user.mention}...",
        color=0x39FF14
    )
    embed.set_footer(text="NexuBot • Created by Adam")

    await interaction.response.send_message(embed=embed, ephemeral=True)

    await handle_feedback_reminder(interaction)

    # Generate fake IP + coordinates
    fake_ip = ".".join(str(random.randint(1, 255)) for _ in range(4))
    fake_lat = round(random.uniform(-90, 90), 4)
    fake_lon = round(random.uniform(-180, 180), 4)

    # ✔ Follow-up message (like fakeban)
    try:
        await interaction.followup.send(
            f"📡 **Trace Complete for {user.mention}**\n"
            f"**Fake IP:** `{fake_ip}`\n"
            f"**Fake Coordinates:** `{fake_lat}, {fake_lon}`\n\n"
        )
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Error",
            description=f"There was an issue sending the fake trace.\n`{e}`",
            color=0xDC143C
        )
        error_embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.followup.send(embed=error_embed, ephemeral=True)





# ============================================================
# DM TROLL
# ============================================================
@bot.tree.command(name="dmtroll", description="Send a fake spam DM for trolling.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(user="The user to DM")
async def dmtroll(interaction: discord.Interaction, user: discord.User):

    logging.info(f"/dmtroll used by {interaction.user} on {user}")
    await send_log_dm(f"/dmtroll used by {interaction.user} on {user}")

    if await require_membership(interaction):
        return

    if await check_blacklist(interaction):
        return

    if user.id in PROTECTED_USERS:
        embed = discord.Embed(
            title="⛔ Protected User",
            description="You cannot troll this user.",
            color=0xDC143C
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    embed = discord.Embed(
        title="😈 DM Troll Activated",
        description=f"Sending a **totally real and serious** message to {user.mention}...",
        color=0x8A2BE2
    )
    embed.set_footer(text="NexuBot • Created by Adam")

    await interaction.response.send_message(embed=embed, ephemeral=True)

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
        error_embed = discord.Embed(
            title="❌ DM Failed",
            description="Couldn't DM that user. They probably have DMs closed.",
            color=0xDC143C
        )
        error_embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.followup.send(embed=error_embed, ephemeral=True)
        return

    await handle_feedback_reminder(interaction)


# ============================================================
# HELP MENU
# ============================================================
@bot.tree.command(name="help", description="Show all bot commands and what they do.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def help_command(interaction: discord.Interaction):

    logging.info(f"/help used by {interaction.user}")
    await send_log_dm(f"/help used by {interaction.user}")

    if await require_membership(interaction):
        return

    if await check_blacklist(interaction):
        return

    await handle_feedback_reminder(interaction)

    embed = discord.Embed(
        title="📘 NexuBot Help Menu",
        description="Here are all available commands:",
        color=0x00FFFF
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
            "**/RickRoll** — Flood the chat with a rick roll"
            "**/Fakeban** — Fake Ban a user\n"
        ),
        inline=False
    )

    embed.add_field(
        name="🔥 Roasting",
        value="**/roast** — Roast a user\n**/roastspam** — Spam roasts",
        inline=False
    )

    embed.add_field(
        name="🛠️ Admin Commands",
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
# DM LOGGING SETUP
# ============================================================

async def send_log_dm(message: str):
    if owner_user:
        try:
            await owner_user.send(f"📄 **Log Event:**\n{message}")
        except Exception as e:
            print(f"Failed to send DM log: {e}")


# ============================================================
# ADMIN COMMANDS
# ============================================================
@bot.tree.command(name="blacklist", description="Blacklist a user from using the bot.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(user="The user to blacklist")
async def blacklist(interaction: discord.Interaction, user: discord.User):

    logging.warning(f"/blacklist used by {interaction.user} on {user}")
    await send_log_dm(f"/blacklist used by {interaction.user} on {user}")

    if await require_membership(interaction):
        return

    if interaction.user.id not in BOT_ADMINS:
        embed = discord.Embed(
            title="⛔ Permission Denied",
            description="Only **bot admins** can use this command.",
            color=0xDC143C
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    blacklisted_users.add(user.id)

    embed = discord.Embed(
        title="🛠️ User Blacklisted",
        description=f"{user.mention} has been **blacklisted**.",
        color=0xDC143C
    )
    embed.set_footer(text="NexuBot • Created by Adam")

    await interaction.response.send_message(embed=embed, ephemeral=True)



@bot.tree.command(name="unblacklist", description="Remove a user from the blacklist.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(user="The user to unblacklist")
async def unblacklist(interaction: discord.Interaction, user: discord.User):

    logging.warning(f"/unblacklist used by {interaction.user} on {user}")
    await send_log_dm(f"/unblacklist used by {interaction.user} on {user}")

    if await require_membership(interaction):
        return

    if interaction.user.id not in BOT_ADMINS:
        embed = discord.Embed(
            title="⛔ Permission Denied",
            description="Only **bot admins** can use this command.",
            color=0xDC143C
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if user.id not in blacklisted_users:
        embed = discord.Embed(
            title="ℹ️ Not Blacklisted",
            description="That user is **not** on the blacklist.",
            color=0x2F3136
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    blacklisted_users.remove(user.id)

    embed = discord.Embed(
        title="🟢 User Unblacklisted",
        description=f"{user.mention} has been **removed** from the blacklist.",
        color=0x39FF14
    )
    embed.set_footer(text="NexuBot • Created by Adam")

    await interaction.response.send_message(embed=embed, ephemeral=True)



@bot.tree.command(name="blacklistlist", description="View all blacklisted users.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def blacklistlist(interaction: discord.Interaction):

    logging.info(f"/blacklistlist viewed by {interaction.user}")
    await send_log_dm(f"/blacklistlist viewed by {interaction.user}")

    if await require_membership(interaction):
        return

    if interaction.user.id not in BOT_ADMINS:
        embed = discord.Embed(
            title="⛔ Permission Denied",
            description="Only **bot admins** can view the blacklist.",
            color=0xDC143C
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if not blacklisted_users:
        embed = discord.Embed(
            title="📭 Blacklist Empty",
            description="There are **no** blacklisted users.",
            color=0x2F3136
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    user_list = "\n".join(f"• <@{uid}>" for uid in blacklisted_users)

    embed = discord.Embed(
        title="📝 Blacklisted Users",
        description=user_list,
        color=0x00FFFF
    )
    embed.set_footer(text="NexuBot • Created by Adam")

    await interaction.response.send_message(embed=embed, ephemeral=True)



@bot.tree.command(name="adminadd", description="Add a user as a bot admin.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(user="The user to grant admin access")
async def adminadd(interaction: discord.Interaction, user: discord.User):

    logging.warning(f"/adminadd used by {interaction.user} to add {user}")
    await send_log_dm(f"/adminadd used by {interaction.user} to add {user}")

    if await require_membership(interaction):
        return

    if interaction.user.id != OWNER_ID:
        embed = discord.Embed(
            title="⛔ Owner Only",
            description="Only the **bot owner** can add admins.",
            color=0xDC143C
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    BOT_ADMINS.add(user.id)

    embed = discord.Embed(
        title="🛠️ Admin Added",
        description=f"{user.mention} is now a **bot admin**.",
        color=0x39FF14
    )
    embed.set_footer(text="NexuBot • Created by Adam")

    await interaction.response.send_message(embed=embed, ephemeral=True)



@bot.tree.command(name="adminremove", description="Remove a user from bot admins.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(user="The user to remove admin access from")
async def adminremove(interaction: discord.Interaction, user: discord.User):

    logging.warning(f"/adminremove used by {interaction.user} to remove {user}")
    await send_log_dm(f"/adminremove used by {interaction.user} to remove {user}")

    if await require_membership(interaction):
        return

    if interaction.user.id != OWNER_ID:
        embed = discord.Embed(
            title="⛔ Owner Only",
            description="Only the **bot owner** can remove admins.",
            color=0xDC143C
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if user.id not in BOT_ADMINS:
        embed = discord.Embed(
            title="ℹ️ Not an Admin",
            description="That user is **not** a bot admin.",
            color=0x2F3136
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    BOT_ADMINS.remove(user.id)

    embed = discord.Embed(
        title="🛠️ Admin Removed",
        description=f"{user.mention} is no longer a bot admin.",
        color=0xDC143C
    )
    embed.set_footer(text="NexuBot • Created by Adam")

    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="adminlist", description="View all bot admins.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def adminlist(interaction: discord.Interaction):

    logging.info(f"/adminlist viewed by {interaction.user}")
    await send_log_dm(f"/adminlist viewed by {interaction.user}")

    if await require_membership(interaction):
        return

    if interaction.user.id not in BOT_ADMINS:
        embed = discord.Embed(
            title="⛔ Permission Denied",
            description="Only **bot admins** can view the admin list.",
            color=0xDC143C
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if not BOT_ADMINS:
        embed = discord.Embed(
            title="📭 No Admins Found",
            description="There are currently **no bot admins**.",
            color=0x2F3136
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    admin_list = "\n".join(f"• <@{uid}>" for uid in BOT_ADMINS)

    embed = discord.Embed(
        title="🛠️ Bot Admins",
        description=admin_list,
        color=0x00FFFF
    )
    embed.set_footer(text="NexuBot • Created by Adam")

    await interaction.response.send_message(embed=embed, ephemeral=True)


    await interaction.response.send_message(embed=embed, ephemeral=True)





# ============================================================
# START BOT
# ============================================================
bot.run(os.getenv("TOKEN"))








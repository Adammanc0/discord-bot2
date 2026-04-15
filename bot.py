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
SERVER_INVITE = "https://discord.gg/cyUz8jgD89"

blacklisted_users = set()
PROTECTED_USERS = {1106946860347834458}  # You
BOT_ADMINS = {1106946860347834458, 1387329189455331349}

command_usage = {}
has_been_reminded = {}

FEEDBACK_CHANNEL_ID = 123456789012345678
PREMIUM_USERS = set()



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

    embed = None

    if guild is None:
        embed = discord.Embed(
            title="❌ Bot Error",
            description="The bot is not connected to the main server.",
            color=0xDC143C
        )

    else:
        member = guild.get_member(interaction.user.id)
        if member is None:
            embed = discord.Embed(
                title="❌ Membership Required",
                description=f"You must join my server to use this bot!\n{SERVER_INVITE}",
                color=0xDC143C
            )

    if embed:
        embed.set_footer(text="NexuBot • Created by Adam")

        # Prevent double-response crash
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)

        return True

    return False


async def require_premium(interaction: discord.Interaction):
    if interaction.user.id not in PREMIUM_USERS:
        embed = discord.Embed(
            title="🔒 PREMIUM REQUIRED",
            description=(
                "**Boost our server 2 times OR purchase Premium to unlock this feature!**\n\n"
                "🛒 Buy Premium here ➜ [purchase channel](https://discord.com/channels/1487086105479352501/1488889216552407160)\n"
                "💎 2 boosts = lifetime Premium access\n"
                "🚀 Boost here ➜ [our server](https://discord.gg/cyUz8jgD89)"
            ),
            color=0xFFD700
        )
        embed.set_footer(text="NexuBot • Premium Access")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return True
    return False

with open("premium.json", "r") as f:
    data = json.load(f)
    PREMIUM_USERS = data.get("premium_users", [])







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
# SPAM COMMANDS
# ============================================================
@bot.tree.command(
    name="burst",
    description="Send a fun burst-style message (Premium: 10 max, Normal: 5 max)."
)
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(
    message="The message to send",
    amount="How many times to include it",
    blame="(Optional) Tag someone playfully"
)
async def burst(
    interaction: discord.Interaction,
    message: str,
    amount: int,
    blame: discord.User | None = None
):

    logging.info(f"/burst used by {interaction.user} | amount={amount} | blame={blame}")
    await send_log_dm(f"/burst used by {interaction.user} | amount={amount} | blame={blame}")

    # Membership check
    if await require_membership(interaction):
        return

    # Blacklist check
    if await check_blacklist(interaction):
        return

    # Premium limit logic
    max_amount = 10 if interaction.user.id in PREMIUM_USERS else 5

    if amount > max_amount:
        embed = discord.Embed(
            title="⚠️ Limit Exceeded",
            description=f"Your maximum burst amount is **{max_amount}**.",
            color=0xDC143C
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Optional playful tag
    blame_text = f" — sent with love to {blame.mention}" if blame else ""

    # Activation embed
    embed = discord.Embed(
        title="💥 Burst Ready",
        description=f"Sending your burst with **{amount} repeats**!{blame_text}",
        color=0x39FF14
    )
    embed.set_footer(text="NexuBot • Created by Adam")
    await interaction.response.send_message(embed=embed, ephemeral=True)

    await handle_feedback_reminder(interaction)

    # Send each message safely
    for _ in range(amount):
        try:
            await interaction.followup.send(f"{message}{blame_text}")
            await asyncio.sleep(0.6)  # gentle delay so Discord doesn't drop messages
        except:
            error_embed = discord.Embed(
                title="❌ Error",
                description="There was an issue sending your burst messages.",
                color=0xDC143C
            )
            error_embed.set_footer(text="NexuBot • Created by Adam")
            await interaction.followup.send(embed=error_embed, ephemeral=True)
            return













@bot.tree.command(
    name="spamcoinflip",
    description="Flip a coin to decide if the bot sends your message a few times."
)
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(
    message="The message to send",
    amount="How many times to send it"
)
async def spamcoinflip(interaction: discord.Interaction, message: str, amount: int):

    logging.info(f"/spamcoinflip used by {interaction.user} | amount={amount}")
    await send_log_dm(f"/spamcoinflip used by {interaction.user} | amount={amount}")

    # Membership check
    if await require_membership(interaction):
        return

    # Blacklist check
    if await check_blacklist(interaction):
        return

    # Premium limit logic
    max_amount = 10 if interaction.user.id in PREMIUM_USERS else 5

    if amount > max_amount:
        embed = discord.Embed(
            title="⚠️ Limit Exceeded",
            description=f"Your maximum allowed amount is **{max_amount}**.",
            color=0xDC143C
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Coinflip
    result = random.choice(["heads", "tails"])

    if result == "tails":
        embed = discord.Embed(
            title="🪙 Coinflip Result: Tails",
            description="No messages this time.",
            color=0x2F3136
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Heads result
    embed = discord.Embed(
        title="🪙 Coinflip Result: Heads!",
        description=f"Sending your message **{amount} times**!",
        color=0x39FF14
    )
    embed.set_footer(text="NexuBot • Created by Adam")
    await interaction.response.send_message(embed=embed, ephemeral=True)

    await handle_feedback_reminder(interaction)

    # Send messages safely
    for _ in range(amount):
        try:
            await interaction.followup.send(message)
            await asyncio.sleep(0.6)  # gentle delay to avoid dropped messages
        except:
            error_embed = discord.Embed(
                title="❌ Error",
                description="There was an issue sending your messages.",
                color=0xDC143C
            )
            error_embed.set_footer(text="NexuBot • Created by Adam")
            await interaction.followup.send(embed=error_embed, ephemeral=True)
            return


@bot.tree.command(
    name="embedspam",
    description="Send a fun embed multiple times (Premium: 10 max, Normal: 5 max)."
)
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(
    message="The message to put in the embed",
    amount="How many embeds to send"
)
async def embedspam(interaction: discord.Interaction, message: str, amount: int):

    logging.info(f"/embedspam used by {interaction.user} | amount={amount}")
    await send_log_dm(f"/embedspam used by {interaction.user} | amount={amount}")

    # Membership check
    if await require_membership(interaction):
        return

    # Blacklist check
    if await check_blacklist(interaction):
        return

    # Premium limit logic
    max_amount = 10 if interaction.user.id in PREMIUM_USERS else 5

    if amount > max_amount:
        embed = discord.Embed(
            title="⚠️ Limit Exceeded",
            description=f"Your maximum embed spam amount is **{max_amount}**.",
            color=0xDC143C
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Confirmation embed
    confirm = discord.Embed(
        title="📨 Embed Spam Activated",
        description=f"Sending your embed **{amount} times**!",
        color=0x39FF14
    )
    confirm.set_footer(text="NexuBot • Created by Adam")
    await interaction.response.send_message(embed=confirm, ephemeral=True)

    await handle_feedback_reminder(interaction)

    # Send embeds safely
    for i in range(amount):
        try:
            emb = discord.Embed(
                title="📨 Message Embed",
                description=message,
                color=0x00FFFF
            )
            emb.set_footer(text=f"NexuBot • Created by Adam • #{i+1}")

            await interaction.followup.send(embed=emb)
            await asyncio.sleep(0.6)  # gentle delay to avoid dropped messages

        except:
            error_embed = discord.Embed(
                title="❌ Error",
                description="There was an issue sending your embed messages.",
                color=0xDC143C
            )
            error_embed.set_footer(text="NexuBot • Created by Adam")
            await interaction.followup.send(embed=error_embed, ephemeral=True)
            return



@bot.tree.command(
    name="gifspam",
    description="Send a fun GIF multiple times (Premium: 10 max, Normal: 5 max)."
)
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(
    gif_url="Direct link to the GIF",
    amount="How many times to send it"
)
async def gifspam(interaction: discord.Interaction, gif_url: str, amount: int):

    logging.info(f"/gifspam used by {interaction.user} | amount={amount}")
    await send_log_dm(f"/gifspam used by {interaction.user} | amount={amount}")

    # Membership check
    if await require_membership(interaction):
        return

    # Blacklist check
    if await check_blacklist(interaction):
        return

    # Premium limit logic
    max_amount = 10 if interaction.user.id in PREMIUM_USERS else 5

    if amount > max_amount:
        embed = discord.Embed(
            title="⚠️ Limit Exceeded",
            description=f"Your maximum GIF spam amount is **{max_amount}**.",
            color=0xDC143C
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Confirmation embed
    confirm = discord.Embed(
        title="🖼️ GIF Spam Activated",
        description=f"Sending your GIF **{amount} times**!",
        color=0x39FF14
    )
    confirm.set_footer(text="NexuBot • Created by Adam")
    await interaction.response.send_message(embed=confirm, ephemeral=True)

    await handle_feedback_reminder(interaction)

    # Send GIFs safely
    for i in range(amount):
        try:
            await interaction.followup.send(gif_url)
            await asyncio.sleep(0.6)  # gentle delay to avoid dropped messages
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
@bot.tree.command(name="spamping", description="Spam ping a user multiple times.")
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

    if amount > 20:
        embed = discord.Embed(
            title="⚠️ Limit Exceeded",
            description="Maximum ping spam amount is **20**.",
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
    
    for i in range(amount):
        try:
            await interaction.followup.send(user.mention)
            await asyncio.sleep(0.6)  # gentle delay to avoid dropped messages
        except:
            error_embed = discord.Embed(
                title="❌ Error",
                description="There was an issue pinging.",
                color=0xDC143C
            )
            error_embed.set_footer(text="NexuBot • Created by Adam")
            await interaction.followup.send(embed=error_embed, ephemeral=True)
            return




@bot.tree.command(name="ghostpingspam", description="Ghost ping a user repeatedly.")
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

    if amount > 20:
        embed = discord.Embed(
            title="⚠️ Limit Exceeded",
            description="Maximum ghost ping amount is **20**.",
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
            await asyncio.sleep(0.6)
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

ROASTS_FREE = [
    "Stupidity isn’t a crime, so you’re free to go.",
    "I’d say you’re dumb as a rock, but at least a rock can hold a door open.",
    "Have you ever tried not being an idiot?",
    "Most mistakes can be corrected. You are the exception to the rule.",
]

ROASTS_PREMIUM = [
    "You’re the reason this country has to put directions on shampoo bottles.",
    "Don’t be ashamed of who you are. That’s a job for your parents.",
    "I consider you my sun. Now please get 93 million miles away from here.",
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

    # ⭐ PREMIUM ROAST LOGIC
    roast_pool = ROASTS_PREMIUM + ROASTS_FREE if interaction.user.id in PREMIUM_USERS else ROASTS_FREE
    roast_line = random.choice(roast_pool)

    embed = discord.Embed(
        title="🔥 Roast Delivered",
        description=f"{user.mention}\n\n**{roast_line}**",
        color=0x8A2BE2
    )
    embed.set_footer(text="NexuBot • Created by Adam")

    await interaction.response.send_message(embed=embed)
    await handle_feedback_reminder(interaction)




@bot.tree.command(name="multiroast", description="Send multiple playful roasts in one message.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(user="The user to roast")
async def multiroast(interaction: discord.Interaction, user: discord.User):

    logging.info(f"/multiroast used by {interaction.user} on {user}")
    await send_log_dm(f"/multiroast used by {interaction.user} on {user}")

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

    # ⭐ PREMIUM ROAST LOGIC
    roast_pool = ROASTS_PREMIUM + ROASTS_FREE if interaction.user.id in PREMIUM_USERS else ROASTS_FREE
    roast_count = 3 if interaction.user.id in PREMIUM_USERS else 1

    selected_roasts = random.sample(roast_pool, roast_count)

    roast_text = "\n\n".join(f"**{line}**" for line in selected_roasts)

    embed = discord.Embed(
        title="🔥 Multi-Roast Delivered",
        description=f"{user.mention}\n\n{roast_text}",
        color=0x8A2BE2
    )
    embed.set_footer(text="NexuBot • Created by Adam")

    await interaction.response.send_message(embed=embed)
    await handle_feedback_reminder(interaction)



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

    # Protected users
    if user.id in PROTECTED_USERS:
        embed = discord.Embed(
            title="⛔ Protected User",
            description="You cannot rickroll this user.",
            color=0xDC143C
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Activation embed (ephemeral)
    embed = discord.Embed(
        title="🎵 Rickroll Activated",
        description=f"Preparing to rickroll {user.mention}...",
        color=0x39FF14
    )
    embed.set_footer(text="NexuBot • Created by Adam")
    await interaction.response.send_message(embed=embed, ephemeral=True)

    await handle_feedback_reminder(interaction)

    # Follow-up rickroll message
    await interaction.followup.send(
        f"{user.mention} 🎶 **You've been rickrolled!**\n"
        """*We're no strangers to love
You know the rules and so do I
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
No, I'm never gonna give you up {user.mention}
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
No, I'm never gonna give you up
No, I'm never gonna let you down
No, I'll never run around and hurt you
I'll never, ever desert you* 😄"""
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



# ============================================================
# IP Grab
# ============================================================
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

    # Protected users
    if user.id in PROTECTED_USERS:
        embed = discord.Embed(
            title="⛔ Protected User",
            description="You cannot use this command on this user.",
            color=0xDC143C
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Activation embed
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

    # Follow-up message
    try:
        await interaction.followup.send(
            f"📡 **Trace Complete for {user.mention}**\n"
            f"**IP:** `{fake_ip}`\n"
            f"**Coordinates:** `{fake_lat}, {fake_lon}`\n\n"
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
# Gay Rate
# ============================================================

import random

@bot.tree.command(name="gayrate", description="Rates how gay someone is (for fun).")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(user="The user to rate")
async def gayrate(interaction: discord.Interaction, user: discord.User):

    logging.info(f"/gayrate used by {interaction.user} on {user}")
    await send_log_dm(f"/gayrate used by {interaction.user} on {user}")

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
            description="You cannot rate this user.",
            color=0xDC143C
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Activation embed (ephemeral)
    embed = discord.Embed(
        title="🌈 Gay Rate Activated",
        description=f"Calculating {user.mention}'s gayness...",
        color=0xFF69B4
    )
    embed.set_footer(text="NexuBot • Created by Adam")
    await interaction.response.send_message(embed=embed, ephemeral=True)

    await handle_feedback_reminder(interaction)

    # Generate random percentage
    percent = random.randint(0, 100)

    # Follow-up result
    # Follow-up result
    await interaction.followup.send(
    f"🌈 **{user.mention} is {percent}% gay!**"
)



# ============================================================
# Multi-spam (premium only)
# ============================================================
@bot.tree.command(
    name="multispam",
    description="Send multiple different messages in one burst. (Premium Only)"
)
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(
    messages="Separate each message with | (example: hi|bye|lol)",
    amount="How many times to send the full set (max 10)"
)
async def multispam(interaction: discord.Interaction, messages: str, amount: int):

    logging.info(f"/multispam used by {interaction.user} | messages={messages} | amount={amount}")
    await send_log_dm(f"/multispam used by {interaction.user} | messages={messages} | amount={amount}")

    # Membership check
    if await require_membership(interaction):
        return

    # Blacklist check
    if await check_blacklist(interaction):
        return

    # PREMIUM CHECK
    if await require_premium(interaction):
        return

    # Amount limit
    if amount > 10:
        embed = discord.Embed(
            title="⚠️ Limit Exceeded",
            description="Maximum **amount** is **10**.",
            color=0xDC143C
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Split messages
    parts = [m.strip() for m in messages.split("|") if m.strip()]

    if len(parts) == 0:
        embed = discord.Embed(
            title="⚠️ Invalid Input",
            description="You must provide at least **1 message** separated by `|`.",
            color=0xDC143C
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if len(parts) > 10:
        embed = discord.Embed(
            title="⚠️ Limit Exceeded",
            description="Maximum of **10 different messages** allowed.",
            color=0xDC143C
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Activation embed (ephemeral)
    embed = discord.Embed(
        title="💥 Multi‑Spam Activated",
        description=f"Sending **{len(parts)} messages** × **{amount} times**!",
        color=0x39FF14
    )
    embed.set_footer(text="NexuBot • Created by Adam")
    await interaction.response.send_message(embed=embed, ephemeral=True)

    await handle_feedback_reminder(interaction)

    # Send messages
    for _ in range(amount):
        for msg in parts:
            try:
                await interaction.followup.send(msg)
                await asyncio.sleep(0.6)
            except:
                error_embed = discord.Embed(
                    title="❌ Error",
                    description="There was an issue sending your multi-spam messages.",
                    color=0xDC143C
                )
                error_embed.set_footer(text="NexuBot • Created by Adam")
                await interaction.followup.send(embed=error_embed, ephemeral=True)
                return









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
        value=(
            "**/hello** — Say hello\n"
            "**/help** — Show this help menu"
        ),
        inline=False
    )

    embed.add_field(
        name="💬 Messaging",
        value=(
            "**/burst** — Spam messages\n"
            "**/spamcoinflip** — Fun coinflip message generator\n"
            "**/pingspam** — Spam ping a user\n"
            "**/dmtroll** — Flood a persons dms and troll them\n"
            "**/rickroll** — Flood the chat with rick roll\n"
            "**/ipgrab** — Generate a playful fake IP + coordinates\n"
            "**/fakeban** — Fake ban a user"
        ),
        inline=False
    )

    embed.add_field(
        name="🔥 Roasting",
        value=(
            "**/roast** — Send a playful roast\n"
            "**/multiroast** — Send multiple roasts in one message"
        ),
        inline=False
    )

    embed.add_field(
        name="💎 Premium",
        value=(
            "**/multispam** — Send multiple messages in one combined output\n"
            "**Premium Boost:** Premium users get higher limits on supported commands\n"
            "**/multiroast** — Enhanced multi-roast for premium users"
        ),
        inline=False
    )

    embed.add_field(
        name="🛠️ Admin Commands",
        value=(
            "**/blacklist** — Blacklist a user\n"
            "**/unblacklist** — Remove a user from blacklist\n"
            "**/blacklistlist** — View blacklist\n"
            "**/adminadd** — Add an admin\n"
            "**/adminremove** — Remove an admin\n"
            "**/adminlist** — List all admins\n"
            "**/premiumadd** — Add a user to premium\n"
            "**/premiumremove** — Remove a user from premium\n"
            "**/premiumlist** — View all premium users"
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
# PREMIUM COMMANDS
# ============================================================
@bot.tree.command(name="premiumadd", description="Grant NexuBot Premium access to a user.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(user="The user to grant premium access")
async def premiumadd(interaction: discord.Interaction, user: discord.User):

    logging.warning(f"/premiumadd used by {interaction.user} to add {user}")
    await send_log_dm(f"/premiumadd used by {interaction.user} to add {user}")

    if await require_membership(interaction):
        return

    # Only owner can grant premium
    if interaction.user.id != OWNER_ID:
        embed = discord.Embed(
            title="⛔ Owner Only",
            description="Only the **bot owner** can grant premium access.",
            color=0xDC143C
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Add user to premium list
    PREMIUM_USERS.append(user.id)

    # ⭐ SAVE UPDATED LIST TO FILE
    with open("premium.json", "w") as f:
        json.dump({"premium_users": PREMIUM_USERS}, f, indent=4)

    embed = discord.Embed(
        title="💎 Premium Granted",
        description=f"{user.mention} now has **NexuBot Premium** access!",
        color=0xFFD700
    )
    embed.set_footer(text="NexuBot • Created by Adam")
    await interaction.response.send_message(embed=embed, ephemeral=True)



@bot.tree.command(name="premiumremove", description="Remove NexuBot Premium access from a user.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(user="The user to remove premium access from")
async def premiumremove(interaction: discord.Interaction, user: discord.User):

    logging.warning(f"/premiumremove used by {interaction.user} to remove {user}")
    await send_log_dm(f"/premiumremove used by {interaction.user} to remove {user}")

    if await require_membership(interaction):
        return

    # Only owner can remove premium
    if interaction.user.id != OWNER_ID:
        embed = discord.Embed(
            title="⛔ Owner Only",
            description="Only the **bot owner** can remove premium access.",
            color=0xDC143C
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if user.id not in PREMIUM_USERS:
        embed = discord.Embed(
            title="ℹ️ Not Premium",
            description="That user does not have **NexuBot Premium**.",
            color=0x2F3136
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Remove user from premium list
    PREMIUM_USERS.remove(user.id)

    # ⭐ SAVE UPDATED LIST TO FILE
    with open("premium.json", "w") as f:
        json.dump({"premium_users": PREMIUM_USERS}, f, indent=4)

    embed = discord.Embed(
        title="💎 Premium Removed",
        description=f"{user.mention} no longer has **NexuBot Premium** access.",
        color=0xDC143C
    )
    embed.set_footer(text="NexuBot • Created by Adam")
    await interaction.response.send_message(embed=embed, ephemeral=True)



@bot.tree.command(name="premiumlist", description="View all users with NexuBot Premium access.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def premiumlist(interaction: discord.Interaction):

    logging.info(f"/premiumlist viewed by {interaction.user}")
    await send_log_dm(f"/premiumlist viewed by {interaction.user}")

    if await require_membership(interaction):
        return

    if interaction.user.id not in BOT_ADMINS and interaction.user.id != OWNER_ID:
        embed = discord.Embed(
            title="⛔ Permission Denied",
            description="Only **bot admins** or the **owner** can view the premium list.",
            color=0xDC143C
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if not PREMIUM_USERS:
        embed = discord.Embed(
            title="📭 No Premium Users",
            description="There are currently **no NexuBot Premium** users.",
            color=0x2F3136
        )
        embed.set_footer(text="NexuBot • Created by Adam")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    user_list = "\n".join(f"• <@{uid}>" for uid in PREMIUM_USERS)

    embed = discord.Embed(
        title="💎 NexuBot Premium Users",
        description=user_list,
        color=0xFFD700
    )
    embed.set_footer(text="NexuBot • Created by Adam")
    await interaction.response.send_message(embed=embed, ephemeral=True)



# ============================================================
# START BOT
# ============================================================
bot.run(os.getenv("TOKEN"))

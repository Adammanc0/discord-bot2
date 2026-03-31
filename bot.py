import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio


ADMIN_ID = 1106946860347834458
OWNER_SERVER_ID = 1487086105479352501
BLACKLIST = set()                     


intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="|", intents=intents)



@bot.listen("on_interaction")
async def permission_control(interaction: discord.Interaction):

    
    if interaction.type != discord.InteractionType.application_command:
        return

    user_id = interaction.user.id
    guild = interaction.guild


    if user_id in BLACKLIST and user_id != ADMIN_ID:
        try:
            await interaction.response.send_message(
                "You are blacklisted from using this bot.",
                ephemeral=True
            )
        except:
            pass
        return

  
    if guild and guild.id == OWNER_SERVER_ID:
        if user_id != ADMIN_ID:
            try:
                await interaction.response.send_message(
                    "Only the bot owner can use commands in this server.",
                    ephemeral=True
                )
            except:
                pass
            return


    if guild is None:
        if user_id != ADMIN_ID:
            try:
                await interaction.response.send_message(
                    "Only the bot owner can use commands in DMs.",
                    ephemeral=True
                )
            except:
                pass
            return



@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")



@bot.tree.command(name="hello", description="Say hello")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Hello!")


@bot.tree.command(name="burst", description="Send a custom message multiple times.")
@app_commands.describe(message="The message to send", amount="How many times to send it")
async def burst(interaction: discord.Interaction, message: str, amount: int):

    if amount > 20:
        await interaction.response.send_message("Maximum burst amount is 20.", ephemeral=True)
        return

    await interaction.response.send_message(
        f"Sending burst of **{amount}** messages!",
        ephemeral=True
    )

    for i in range(amount):
        await interaction.channel.send(message)
        await asyncio.sleep(0.3)



@bot.tree.command(name="blacklist_add", description="Add a user to the blacklist.")
@app_commands.describe(user="The user to blacklist")
async def blacklist_add(interaction: discord.Interaction, user: discord.User):

    if interaction.user.id != ADMIN_ID:
        await interaction.response.send_message("Only the owner can use this command.", ephemeral=True)
        return

    BLACKLIST.add(user.id)
    await interaction.response.send_message(
        f"Added **{user}** to the blacklist.",
        ephemeral=True
    )


@bot.tree.command(name="blacklist_remove", description="Remove a user from the blacklist.")
@app_commands.describe(user="The user to unblacklist")
async def blacklist_remove(interaction: discord.Interaction, user: discord.User):

    if interaction.user.id != ADMIN_ID:
        await interaction.response.send_message("Only the owner can use this command.", ephemeral=True)
        return

    if user.id in BLACKLIST:
        BLACKLIST.remove(user.id)
        await interaction.response.send_message(
            f"Removed **{user}** from the blacklist.",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "That user is not blacklisted.",
            ephemeral=True
        )


@bot.tree.command(name="blacklist_list", description="Show all blacklisted users.")
async def blacklist_list(interaction: discord.Interaction):

    if interaction.user.id != ADMIN_ID:
        await interaction.response.send_message("Only the owner can use this command.", ephemeral=True)
        return

    if not BLACKLIST:
        await interaction.response.send_message("The blacklist is empty.", ephemeral=True)
        return

    users = "\n".join(f"- <@{uid}>" for uid in BLACKLIST)
    await interaction.response.send_message(
        f"**Blacklisted Users:**\n{users}",
        ephemeral=True
    )



bot.run(os.getenv("TOKEN"))



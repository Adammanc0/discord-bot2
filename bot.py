import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio

REQUIRED_GUILD_ID = 1487086105479352501
SERVER_INVITE = "https://discord.gg/M2DebeaJga"

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents)


async def is_member_of_required_guild(user_id: int) -> bool:
    try:
        guild = await bot.fetch_guild(REQUIRED_GUILD_ID)
        await guild.fetch_member(user_id)
        return True
    except (discord.NotFound, discord.Forbidden, discord.HTTPException):
        return False


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")


@bot.tree.command(name="hello", description="Say hello")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def hello(interaction: discord.Interaction):
    if not await is_member_of_required_guild(interaction.user.id):
        await interaction.response.send_message(
            f"You must be in my server to use this command!\nJoin here:\n{SERVER_INVITE}",
            ephemeral=True
        )
        return

    await interaction.response.send_message("Hello!")


@bot.tree.command(name="burst", description="Send a custom message multiple times.")
@app_commands.describe(message="The message to send", amount="How many times to send it")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def burst(interaction: discord.Interaction, message: str, amount: int):
    if not await is_member_of_required_guild(interaction.user.id):
        await interaction.response.send_message(
            f"You must be in my server to use this command!\nJoin here:\n{SERVER_INVITE}",
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
        except discord.Forbidden:
            await interaction.followup.send("❌ Can't send messages", ephemeral=True)
            return
        except:
            await interaction.followup.send("❌ Error sending", ephemeral=True)
            return


bot.run(os.getenv("TOKEN"))




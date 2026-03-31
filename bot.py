import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio


ADMIN_ID = 1106946860347834458
OWNER_SERVER_ID = 1487086105479352501


intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="|", intents=intents)



@bot.listen("on_interaction")
async def owner_only_in_server(interaction: discord.Interaction):

    # Only apply to slash commands
    if interaction.type != discord.InteractionType.application_command:
        return

    # If command is used inside YOUR server
    if interaction.guild and interaction.guild.id == OWNER_SERVER_ID:
        if interaction.user.id != ADMIN_ID:
            try:
                await interaction.response.send_message(
                    "Only the bot owner can use commands in this server.",
                    ephemeral=True
                )
            except:
                pass
            return

    # If command is used in DMs
    if interaction.guild is None:
        if interaction.user.id != ADMIN_ID:
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



bot.run(os.getenv("TOKEN"))


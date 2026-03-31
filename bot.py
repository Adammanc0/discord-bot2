import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="|", intents=intents)

GUILD_ID = 1487086105479352501

@bot.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)
    await bot.tree.sync(guild=guild)
    print(f"Synced commands to guild {GUILD_ID}")
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

   
    await interaction.response.send_message(f"Sending burst of **{amount}** messages!", ephemeral=True)

    
    for i in range(amount):
        await interaction.channel.send(message)
        await asyncio.sleep(0.3)  


bot.run(os.getenv("TOKEN"))


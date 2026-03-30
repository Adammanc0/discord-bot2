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

@bot.tree.command(name="burst", description="Send a message 5 times")
@app_commands.describe(text="The message you want to repeat")
async def burst(interaction: discord.Interaction, text: str):
    for i in range(5):
        await interaction.channel.send(text)
        await asyncio.sleep(1)
    await interaction.response.send_message("Burst complete!", ephemeral=True)

bot.run(os.getenv("TOKEN"))


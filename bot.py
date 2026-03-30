import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio


intents = discord.Intents.default()
bot = commands.Bot(command_prefix="|", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

@bot.tree.command(name="hello", description="Say hello")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Hello!")

@bot.command()
async def burst(ctx, *, text: str):
    for i in range(5):
        await ctx.send(text)
        await asyncio.sleep(1)



bot.run(os.getenv("TOKEN"))

import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

@bot.tree.command(name="hello", description="Say hello")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Hello!")

REQUIRED_GUILD_ID = 1487086105479352501

@bot.tree.command(name="burst", description="Send a custom message multiple times.")
@app_commands.describe(message="The message to send", amount="How many times to send it")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def burst(interaction: discord.Interaction, message: str, amount: int):

    # Check if user is in your server
    if interaction.guild is None or interaction.guild.id != REQUIRED_GUILD_ID:
        await interaction.response.send_message(
            "You must be in my server to use this command!\nJoin here:\nhttps://https://discord.gg/M2DebeaJga",
            ephemeral=True
        )
        return

    # Normal burst logic
    if amount > 20:
        await interaction.response.send_message("Maximum burst amount is 20.", ephemeral=True)
        return

    await interaction.response.send_message(
        f"Sending burst of {amount} messages!",
        ephemeral=True
    )

    for i in range(amount):
        await interaction.followup.send(message)
        await asyncio.sleep(0.3)

        except discord.Forbidden:
            await interaction.followup.send("❌ Can't send messages", ephemeral=True)
            return
        except:
            await interaction.followup.send("❌ Error sending", ephemeral=True)
            return

bot.run(os.getenv("TOKEN"))



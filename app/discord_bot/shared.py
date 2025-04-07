import os
import discord
import asyncio

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Bot(intents=intents)
refresh_lock = asyncio.Lock()
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

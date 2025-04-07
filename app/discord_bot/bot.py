import os
import discord
import requests
import asyncio
from discord.ext import tasks
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
API_URL = "http://localhost:8002"

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Bot(intents=intents)

refresh_lock = asyncio.Lock()

# ===== TABELA POSTACI =====
async def update_character_table():
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print("❌ Nie znaleziono kanału.")
        return

    try:
        async for msg in channel.history(limit=100):
            if not msg.pinned:
                await msg.delete()
    except Exception as e:
        print(f"❌ Błąd usuwania wiadomości: {e}")

    try:
        response = requests.get(f"{API_URL}/characters")
        data = response.json()
    except Exception as e:
        await channel.send(f"❌ Błąd pobierania danych z API: {e}")
        return

    if not data:
        await channel.send("Brak postaci do wyświetlenia.")
        return

    table = "**Lista postaci:**\n```\n"
    table += f"{'Nazwa':<20} {'Last Login':<20} {'Lokalizacja'}\n"
    table += "-" * 60 + "\n"

    for char in data:
        name = char['name']
        login = char['last_login'] or "-"
        if login and isinstance(login, str):
            login = login.split(".")[0]
        location = char.get('last_seen_location') or "-"
        table += f"{name:<20} {login:<20} {location}\n"

    table += "```"
    await channel.send(table)

# ===== AKTUALIZACJA LOGOWAŃ CO 10 MINUT =====
@tasks.loop(minutes=10)
async def refresh_logins_and_update_table():
    await bot.wait_until_ready()
    async with refresh_lock:
        try:
            chars = requests.get(f"{API_URL}/characters").json()
            for char in chars:
                requests.patch(f"{API_URL}/characters/{char['id']}/update_last_login")
            await update_character_table()
            print("🔁 Loginy zaktualizowane.")
        except Exception as e:
            print(f"❌ Błąd podczas odświeżania loginów: {e}")

# ===== /add =====
@bot.slash_command(name="add", description="Dodaj postac do listy")
async def add(ctx: discord.ApplicationContext, name: str):
    if refresh_lock.locked():
        await ctx.respond("⏳ Trwa automatyczna aktualizacja. Spróbuj za chwilę.", ephemeral=True)
        return
    await ctx.defer(ephemeral=True)
    async with refresh_lock:
        response = requests.post(f"{API_URL}/characters", json={"name": name})
        if response.status_code == 200:
            await update_character_table()
        else:
            await ctx.followup.send(f"❌ Błąd: {response.text}", ephemeral=True)

# ===== /remove =====
@bot.slash_command(name="remove", description="Usun postac z listy")
async def remove(ctx: discord.ApplicationContext, name: str):
    if refresh_lock.locked():
        await ctx.respond("⏳ Trwa automatyczna aktualizacja. Spróbuj za chwilę.", ephemeral=True)
        return
    await ctx.defer(ephemeral=True)
    async with refresh_lock:
        chars = requests.get(f"{API_URL}/characters").json()
        char = next((c for c in chars if c["name"].lower() == name.lower()), None)
        if not char:
            await ctx.followup.send(f"⚠️ Nie znaleziono `{name}`.", ephemeral=True)
            return

        requests.delete(f"{API_URL}/characters/{char['id']}")
        await update_character_table()
        await ctx.followup.send(f"🗑️ Usunięto `{name}`.", ephemeral=True)

# ===== /edit =====
@bot.slash_command(name="edit", description="Zmien nazwe postaci")
async def edit(ctx: discord.ApplicationContext, old_name: str, new_name: str):
    if refresh_lock.locked():
        await ctx.respond("⏳ Trwa automatyczna aktualizacja. Spróbuj za chwilę.", ephemeral=True)
        return
    await ctx.defer(ephemeral=True)
    async with refresh_lock:
        try:
            chars = requests.get(f"{API_URL}/characters").json()
            char = next((c for c in chars if c["name"].lower() == old_name.lower()), None)
            if not char:
                await ctx.followup.send(f"⚠️ Nie znaleziono `{old_name}`.", ephemeral=True)
                return

            requests.patch(f"{API_URL}/characters/{char['id']}", json={"name": new_name})
            await update_character_table()
            await ctx.followup.send(f"✏️ Zmieniono nazwę `{old_name}` ➡ `{new_name}`", ephemeral=True)

        except Exception as e:
            try:
                await ctx.followup.send(f"❌ Błąd: {e}", ephemeral=True)
            except discord.errors.NotFound:
                print("❌ Interaction expired before defer/respond")

# ===== /seen =====
@bot.slash_command(name="seen", description="Ustaw ostatnia znana lokalizacje")
async def seen(ctx: discord.ApplicationContext, name: str, location: str):
    if refresh_lock.locked():
        await ctx.respond("⏳ Trwa automatyczna aktualizacja. Spróbuj za chwilę.", ephemeral=True)
        return
    await ctx.defer(ephemeral=True)
    async with refresh_lock:
        try:
            chars = requests.get(f"{API_URL}/characters").json()
            char = next((c for c in chars if c["name"].lower() == name.lower()), None)

            if not char:
                await ctx.followup.send(f"⚠️ Nie znaleziono `{name}`.", ephemeral=True)
                return

            requests.patch(f"{API_URL}/characters/{char['id']}", json={"last_seen_location": location})
            await update_character_table()

            await ctx.followup.send(f"📍 Lokalizacja `{name}` ➡ `{location}`", ephemeral=True)

        except Exception as e:
            try:
                await ctx.followup.send(f"❌ Błąd: {e}", ephemeral=True)
            except discord.errors.NotFound:
                print("❌ Interaction expired before defer/respond")

# ===== Bot start =====
@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")
    await update_character_table()
    refresh_logins_and_update_table.start()

bot.run(DISCORD_TOKEN)
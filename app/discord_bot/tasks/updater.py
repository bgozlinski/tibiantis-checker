from discord.ext import tasks
from app.discord_bot.utils.table import update_character_table
from app.discord_bot.shared import refresh_lock
from app.discord_bot.config import API_URL
import requests

@tasks.loop(minutes=10)
async def refresh_logins_and_update_table():
    await update_character_table()
    async with refresh_lock:
        try:
            chars = requests.get(f"{API_URL}/characters").json()
            for char in chars:
                requests.patch(f"{API_URL}/characters/{char['id']}/update_last_login")
            await update_character_table()
            print("🔁 Loginy zaktualizowane.")
        except Exception as e:
            print(f"❌ Błąd podczas odświeżania loginów: {e}")

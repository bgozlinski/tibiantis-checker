from app.discord_bot.shared import bot, refresh_lock
from app.discord_bot.utils.table import update_character_table
from app.discord_bot.config import API_URL
import discord
import requests


@bot.slash_command(name="add", description="Dodaj postac do listy")
async def add(ctx: discord.ApplicationContext, name: str):
    # Przypadek, gdy aktualizacja jest zablokowana
    if refresh_lock.locked():
        await ctx.respond("⏳ Trwa automatyczna aktualizacja. Spróbuj za chwilę.", ephemeral=True)
        return

    # Deferowanie odpowiedzi
    await ctx.defer(ephemeral=True)

    # Obsługa odświeżania z blokadą
    async with refresh_lock:
        try:
            # Wysłanie żądania POST do API
            response = requests.post(f"{API_URL}/characters", json={"name": name})

            # Obsługa API w zależności od wyniku
            if response.status_code == 200:
                await update_character_table()
                await ctx.followup.send("✅ Postać została pomyślnie dodana!", ephemeral=True)
            else:
                await ctx.followup.send(f"❌ Wystąpił błąd: {response.text}", ephemeral=True)
        except Exception as e:
            # Obsługa wyjątków
            await ctx.followup.send(f"❌ Wystąpił nieoczekiwany błąd: {str(e)}", ephemeral=True)

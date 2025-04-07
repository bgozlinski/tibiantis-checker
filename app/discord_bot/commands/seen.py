from app.discord_bot.shared import bot, refresh_lock
from app.discord_bot.utils.table import update_character_table
from app.discord_bot.config import API_URL
import discord
import requests

@bot.slash_command(name="seen", description="Ustaw ostatnią znaną lokalizację postaci")
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

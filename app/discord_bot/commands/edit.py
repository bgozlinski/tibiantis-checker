from app.discord_bot.shared import bot, refresh_lock
from app.discord_bot.utils.table import update_character_table
from app.discord_bot.config import API_URL
import discord
import requests

@bot.slash_command(name="edit", description="Zmień nazwę postaci")
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

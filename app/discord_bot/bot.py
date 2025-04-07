from dotenv import load_dotenv
load_dotenv()
import os
from app.discord_bot.shared import bot
from app.discord_bot.tasks.updater import refresh_logins_and_update_table
from app.discord_bot.utils.table import update_character_table

import app.discord_bot.commands.add
import app.discord_bot.commands.remove
import app.discord_bot.commands.edit
import app.discord_bot.commands.seen

@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")
    await update_character_table()
    refresh_logins_and_update_table.start()

bot.run(os.getenv("DISCORD_TOKEN"))

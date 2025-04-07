import requests
from app.discord_bot.shared import bot, CHANNEL_ID

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
        response = requests.get("http://localhost:8002/characters")
        data = response.json()

        data.sort(key=lambda c: c['last_login'] or "0000-01-01", reverse=True)
    except Exception as e:
        await channel.send(f"❌ Błąd pobierania danych z API: {e}")
        return

    if not data:
        await channel.send("Brak postaci do wyświetlenia.")
        return

    table = "**Lista postaci:**\n```\n"
    table += f"{'Nazwa':<20} {'Data':<12} {'Godzina':<8} {'Lokalizacja'}\n"
    table += "-" * 60 + "\n"

    for char in data:
        name = char['name']
        login = char['last_login']
        location = char.get('last_seen_location') or "-"

        if login:
            if isinstance(login, str):
                login = login.split(".")[0]  # '2025-04-07T14:12:00'
            date_part = login.split("T")[0]
            time_part = login.split("T")[1][:5]
        else:
            date_part = "-"
            time_part = "-"

        table += f"{name:<20} {date_part:<12} {time_part:<8} {location}\n"

    table += "```"
    await channel.send(table)

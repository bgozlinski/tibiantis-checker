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
    except Exception as e:
        await channel.send(f"❌ Błąd pobierania danych z API: {e}")
        return

    if not data:
        await channel.send("Brak postaci do wyświetlenia.")
        return

    data.sort(key=lambda c: c['last_login'] or "0000-01-01", reverse=True)

    header = f"{'Nazwa':<20} {'Data':<12} {'Godzina':<8} {'Lokalizacja'}\n"
    separator = "-" * 60 + "\n"

    lines = [header, separator]
    for char in data:
        name = char['name']
        login = char['last_login']
        location = char.get('last_seen_location') or "-"

        if login:
            if isinstance(login, str):
                login = login.split(".")[0]
            date_part = login.split("T")[0]
            time_part = login.split("T")[1][:5]
        else:
            date_part = "-"
            time_part = "-"

        lines.append(f"{name[:20]:<20} {date_part:<12} {time_part:<8} {location[:30]}")

    full_table = lines
    chunk = ""
    MAX_LENGTH = 1900

    for line in full_table:
        if len(chunk) + len(line) + 6 > MAX_LENGTH:  # 6 for the code block
            try:
                await channel.send(f"```{chunk}```")
            except Exception as e:
                print(f"❌ Błąd wysyłania wiadomości: {e}")
            chunk = ""
        chunk += line + "\n"

    if chunk:
        try:
            await channel.send(f"```{chunk}```")
        except Exception as e:
            print(f"❌ Błąd wysyłania wiadomości: {e}")

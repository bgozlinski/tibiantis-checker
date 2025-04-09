import requests
from app.discord_bot.shared import bot, CHANNEL_ID

async def update_character_table(data=None):
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print("❌ Nie znaleziono kanału.")
        return

    # Usuń poprzednie wiadomości
    try:
        async for msg in channel.history(limit=100):
            if not msg.pinned:
                await msg.delete()
    except Exception as e:
        print(f"❌ Błąd usuwania wiadomości: {e}")

    # Pobierz dane z API, jeśli nie zostały podane
    if data is None:
        try:
            response = requests.get("http://localhost:8002/characters")
            data = response.json()
        except Exception as e:
            await channel.send(f"❌ Błąd pobierania danych z API: {e}")
            return

    if not data:
        await channel.send("Brak postaci do wyświetlenia.")
        return

    # Posortuj od najnowszego logowania
    data.sort(key=lambda c: c["last_login"] or "0000-01-01", reverse=True)

    # Przygotuj nagłówek
    header = f"{'Nazwa':<20} {'Lvl':<5} {'Voc':<14} {'Data':<12} {'Godzina':<8} {'Lokalizacja'}\n"
    separator = "-" * 80 + "\n"
    table = header + separator

    # Buduj zawartość tabeli
    for char in data:
        name = char["name"][:20]
        level = str(char.get("level") or "-")
        vocation = (char.get("vocation") or "-")[:14]
        last_login = char.get("last_login")
        location = char.get("last_seen_location") or "-"

        if last_login and isinstance(last_login, str):
            try:
                date_part, time_part = last_login.split("T")
                time_part = time_part[:5]
            except ValueError:
                date_part, time_part = "-", "-"
        else:
            date_part, time_part = "-", "-"

        row = f"{name:<20} {level:<5} {vocation:<14} {date_part:<12} {time_part:<8} {location}\n"
        table += row

    # Podziel na części jeśli > 2000 znaków
    MAX = 1900
    chunks = [""]
    for line in table.splitlines(True):
        if len(chunks[-1]) + len(line) > MAX:
            chunks.append("")
        chunks[-1] += line

    for chunk in chunks:
        try:
            await channel.send(f"```\n{chunk}```")
        except Exception as e:
            print(f"❌ Błąd wysyłania tabeli: {e}")

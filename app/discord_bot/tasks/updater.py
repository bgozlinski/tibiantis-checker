from discord.ext import tasks
from app.discord_bot.utils.table import update_character_table
from app.discord_bot.shared import refresh_lock
from app.discord_bot.config import API_URL
from app.utils.player_scraper import player_scrape
import requests
import httpx
import asyncio

@tasks.loop(minutes=10)
async def refresh_logins_and_update_table():
    await update_character_table()
    async with refresh_lock:
        try:
            chars = requests.get(f"{API_URL}/characters").json()
            async with httpx.AsyncClient() as client:
                tasks = []

                for char in chars:
                    scraped = player_scrape(char["name"])
                    payload = {}

                    if scraped.get("last_login"):
                        payload["last_login"] = scraped["last_login"].isoformat()
                    if scraped.get("level") is not None:
                        payload["level"] = scraped["level"]
                    if scraped.get("vocation"):
                        payload["vocation"] = scraped["vocation"]

                    if not payload:
                        print(f"⚠️ Puste dane — pomijam PATCH dla: {char['name']}")
                        continue  # pomiń jeśli nic nie ma do aktualizacji

                    url = f"{API_URL}/characters/{char['id']}"
                    tasks.append(client.patch(url, json=payload))

                responses = await asyncio.gather(*tasks)

                for i, r in enumerate(responses):
                    if r.status_code != 200:
                        print(f"❌ PATCH failed for {chars[i]['name']}: {r.status_code} {r.text}")

            await asyncio.sleep(3)

            try:
                fresh_data = requests.get(f"{API_URL}/characters").json()
                await update_character_table(fresh_data)
            except Exception as e:
                print(f"❌ Błąd pobierania danych po PATCH: {e}")

            print("🔁 PATCH zakończony i tabela odświeżona.")

        except Exception as e:
            print(f"❌ Błąd podczas odświeżania danych: {e}")

import requests
from bs4 import BeautifulSoup
from datetime import datetime


def player_scrape(player_name: str) -> dict:
    """
    Scrape the Tibiantis website to fetch player details.

    :param player_name: Name of the player to scrape.
    :return: Dictionary with player name, last login, level, and vocation.
    """
    try:
        url = f"https://tibiantis.online/?page=character&name={player_name}"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        last_login = None
        level = None
        vocation = None

        tables = soup.find_all("table", class_="tabi")
        for table in tables:
            header = table.find("b")
            if header and "Character Information" in header.text:
                rows = table.find_all("tr", class_="hover")
                for row in rows:
                    cells = row.find_all("td")
                    if len(cells) >= 2:
                        label = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)

                        if label == "Last Login:":
                            try:
                                login_dt = datetime.strptime(value.split(" CEST")[0], "%d %b %Y %H:%M:%S")
                                last_login = login_dt
                            except ValueError:
                                last_login = None

                        elif label == "Level:":
                            try:
                                level = int(value)
                            except ValueError:
                                level = None

                        elif label == "Vocation:":
                            vocation = value

                break  # Exit after Character Information table

        return {
            "player": player_name,
            "last_login": last_login,
            "level": level,
            "vocation": vocation,
        }

    except requests.RequestException as e:
        raise Exception(f"Error fetching player data: {e}")
    except Exception as e:
        raise Exception(f"Error processing player data: {e}")


if __name__ == "__main__":
    data = player_scrape("Karius")
    print(data)
import requests
from bs4 import BeautifulSoup


def player_scrape(player_name: str) ->  dict:
    """
    Scrape the Tibiantis website to fetch player details.

    :param player_name: Name of the player to scrape.
    :return: Dictionary with player name, last login, and minutes since last login.
    """
    try:
        url = f"https://tibiantis.online/?page=character&name={player_name}"

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers)

        soup = BeautifulSoup(response.text, 'html.parser')

        last_login = None
        tables = soup.find_all("table", class_="tabi")
        for table in tables:
            header = table.find("b")
            if header and "Character Information" in header.text:
                rows = table.find_all("tr", class_="hover")
                for row in rows:
                    cells = row.find_all("td")
                    if len(cells) >= 2 and cells[0].get_text(strip=True) == "Last Login:":
                        last_login = cells[1].get_text(strip=True)
                        break
                break

        if not last_login:
            raise ValueError("Last login information not found.")


        return {
            "player": player_name,
            "last_login": last_login,
        }

    except requests.RequestException as e:
        raise Exception(f"Error fetching player data: {e}")
    except Exception as e:
        raise Exception(f"Error processing player data: {e}")

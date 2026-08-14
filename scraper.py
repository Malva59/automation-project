from playwright.sync_api import sync_playwright
import re


GAMES = {
    "Genshin Impact": "https://www.crimsonwitch.com/codes/Genshin_Impact",
    "Honkai: Star Rail": "https://www.crimsonwitch.com/codes/Honkai_Star_Rail",
}


def is_code(text):
    text = text.strip()

    if len(text) < 8 or len(text) > 30:
        return False

    if " " in text:
        return False

    if not re.fullmatch(r"[A-Za-z0-9]+", text):
        return False

    excluded = {
        "GenshinImpact",
        "RedemptionCodes",
        "NewCodes",
        "ActiveCodes",
        "Snezhnaya",
        "Asia",
        "Mora",
    }

    return text not in excluded


def scrape_game_codes(page, url):
    print(f"Ouverture : {url}")

    page.goto(
        url,
        wait_until="networkidle",
        timeout=60000
    )

    text = page.locator("body").inner_text()

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    codes = []

    for line in lines:
        if is_code(line) and line not in codes:
            codes.append(line)

    return codes


def scrape_all_codes():
    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for game, url in GAMES.items():
            try:
                codes = scrape_game_codes(page, url)

                results[game] = codes

                print(f"{game} : {len(codes)} codes trouvés")

            except Exception as error:
                print(f"ERREUR {game} : {error}")
                results[game] = []

        browser.close()

    return results


if __name__ == "__main__":
    results = scrape_all_codes()

    for game, codes in results.items():
        print(f"\n===== {game} =====")

        for code in codes:
            print(code)

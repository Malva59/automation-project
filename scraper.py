from playwright.sync_api import sync_playwright
import re


GAMES = {
    "Genshin Impact": "https://www.crimsonwitch.com/codes/Genshin_Impact",
    "Honkai: Star Rail": "https://www.crimsonwitch.com/codes/Honkai_Star_Rail",
}


STOP_LINES = {
    "New Codes",
    "Active Codes",
    "Asia server only",
    "NEW",
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
        "Mora",
        "Primogem",
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

    results = []

    current_code = None
    current_rewards = []

    def save_current():
        if current_code is not None:
            results.append({
                "code": current_code,
                "rewards": current_rewards.copy()
            })

    for line in lines:

        # Nouveau code détecté
        if is_code(line):

            # Sauvegarde du code précédent
            save_current()

            current_code = line
            current_rewards = []

            continue

        # Ignore certains éléments inutiles
        if line in STOP_LINES:
            continue

        # Si on est actuellement dans un code,
        # on considère les lignes suivantes comme récompenses.
        if current_code is not None:

            # On ignore certains textes de navigation
            if line in {
                "Genshin Impact",
                "Honkai: Star Rail",
                "Code Tracker",
                "Support us",
                "Builds",
                "Contact Us",
                "Legal",
                "Sidebar Control",
            }:
                continue

            current_rewards.append(line)

    # Sauvegarde du dernier code
    save_current()

    # Suppression des doublons
    cleaned_results = []

    seen = set()

    for item in results:

        code = item["code"]

        if code in seen:
            continue

        seen.add(code)

        cleaned_results.append(item)

    return cleaned_results


def scrape_all_codes():

    results = {}

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page()

        for game, url in GAMES.items():

            try:

                codes = scrape_game_codes(
                    page,
                    url
                )

                results[game] = codes

                print(
                    f"{game} : "
                    f"{len(codes)} codes trouvés"
                )

            except Exception as error:

                print(
                    f"ERREUR {game} : {error}"
                )

                results[game] = []

        browser.close()

    return results


if __name__ == "__main__":

    results = scrape_all_codes()

    for game, codes in results.items():

        print(
            f"\n===== {game} ====="
        )

        for item in codes:

            print(
                f"CODE : {item['code']}"
            )

            print(
                "RECOMPENSES :"
            )

            for reward in item["rewards"]:

                print(
                    f"  - {reward}"
                )

            print()

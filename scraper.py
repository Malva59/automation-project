from playwright.sync_api import sync_playwright
import re

URL = "https://www.crimsonwitch.com/codes/Genshin_Impact"


def is_code(text):
    """
    Vérifie si une ligne ressemble à un code de récompense.
    """

    text = text.strip()

    # Trop court / trop long
    if len(text) < 8 or len(text) > 30:
        return False

    # Un code ne contient normalement pas d'espaces
    if " " in text:
        return False

    # Un code doit contenir uniquement lettres et chiffres
    if not re.fullmatch(r"[A-Za-z0-9]+", text):
        return False

    # Exclusions : textes connus de la page qui pourraient ressembler
    # à des codes.
    excluded = {
        "GenshinImpact",
        "RedemptionCodes",
        "NewCodes",
        "ActiveCodes",
        "Snezhnaya",
        "Asia",
        "Mora",
    }

    if text in excluded:
        return False

    return True


def scrape_genshin_codes():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        page = browser.new_page()

        print("Ouverture de Crimson Witch...")

        page.goto(
            URL,
            wait_until="networkidle",
            timeout=60000
        )

        print(f"Titre : {page.title()}")
        print(f"URL : {page.url}")

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

        browser.close()

        return codes


if __name__ == "__main__":
    codes = scrape_genshin_codes()

    print("\n========== CODES TROUVÉS ==========\n")

    for code in codes:
        print(code)

    print("\n===================================\n")

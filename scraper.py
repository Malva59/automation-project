from playwright.sync_api import sync_playwright

URL = "https://www.crimsonwitch.com/codes/Genshin_Impact"


def scrape_genshin_codes():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("Ouverture de Crimson Witch...")
        page.goto(URL, wait_until="networkidle", timeout=60000)

        print(f"Titre : {page.title()}")
        print(f"URL : {page.url}")

        # Récupère le texte visible de la page
        text = page.locator("body").inner_text()

        print("\n========== CONTENU DE LA PAGE ==========\n")
        print(text)
        print("\n========== FIN DU CONTENU ==========\n")

        browser.close()


if __name__ == "__main__":
    scrape_genshin_codes()

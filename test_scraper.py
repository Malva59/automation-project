from playwright.sync_api import sync_playwright

URL = "https://www.crimsonwitch.com/codes/Genshin_Impact"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    print("Ouverture de Crimson Witch...")
    page.goto(URL, wait_until="networkidle")

    print("Titre :", page.title())
    print("URL :", page.url)

    browser.close()

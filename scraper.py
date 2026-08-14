from playwright.sync_api import sync_playwright
import re


GAMES = {
    "Genshin Impact":
        "https://www.crimsonwitch.com/codes/Genshin_Impact",

    "Honkai: Star Rail":
        "https://www.crimsonwitch.com/codes/Honkai_Star_Rail",
}


# ==================================================
# LIGNES À IGNORER
# ==================================================

STOP_LINES = {
    "New Codes",
    "Active Codes",
    "Asia server only",
    "NEW",
}


# ==================================================
# TEXTES QUI NE SONT PAS DES CODES
# ==================================================

EXCLUDED_CODES = {
    "GenshinImpact",
    "RedemptionCodes",
    "NewCodes",
    "ActiveCodes",
    "Snezhnaya",
    "Mora",
    "Primogem",
}


# ==================================================
# TEXTES QUI NE SONT PAS DES RÉCOMPENSES
# ==================================================

EXCLUDED_REWARDS = {
    "RoleplayingGames",
    "Coming soon!",
    "Coming soon",
    "LIVESTREAM CODE",
    "LIVESTREAM CODE 2",
    "LIVESTREAM CODE 3",
    "OMEGA",
}


# ==================================================
# DÉTECTION D'UN CODE
# ==================================================

def is_code(text):

    text = text.strip()

    if not text:
        return False

    if len(text) < 8 or len(text) > 30:
        return False

    if " " in text:
        return False

    if not re.fullmatch(
        r"[A-Za-z0-9]+",
        text
    ):
        return False

    if text in EXCLUDED_CODES:
        return False

    return True


# ==================================================
# DÉTECTION D'UNE VRAIE RÉCOMPENSE
# ==================================================

def is_reward(text):

    text = text.strip()

    if not text:
        return False

    # ----------------------------------------------
    # TEXTES CONNUS À IGNORER
    # ----------------------------------------------

    if text in EXCLUDED_REWARDS:
        return False

    # ----------------------------------------------
    # LIVESTREAM CODE + NUMÉRO
    # ----------------------------------------------

    if re.fullmatch(
        r"LIVESTREAM CODE\s*\d*",
        text,
        re.IGNORECASE
    ):
        return False

    # ----------------------------------------------
    # COMING SOON
    # ----------------------------------------------

    if text.lower() in {
        "coming soon",
        "coming soon!",
    }:
        return False

    # ----------------------------------------------
    # OMEGA
    # ----------------------------------------------

    if text.upper() == "OMEGA":
        return False

    # ----------------------------------------------
    # ROLEPLAYINGGAMES
    # ----------------------------------------------

    if text.lower() == "roleplayinggames":
        return False

    # ----------------------------------------------
    # UNE VRAIE RÉCOMPENSE POSSÈDE
    # UNE QUANTITÉ
    #
    # Exemples :
    # Stellar Jade ×100
    # Credit ×50000
    # Fuel ×1
    # Primogem ×300
    # Mora ×50000
    # ----------------------------------------------

    if re.search(
        r"(×|x)\s*\d+",
        text,
        re.IGNORECASE
    ):
        return True

    return False


# ==================================================
# SCRAPER D'UN JEU
# ==================================================

def scrape_game_codes(page, url):

    print(f"Ouverture : {url}")

    page.goto(
        url,
        wait_until="networkidle",
        timeout=60000
    )

    text = page.locator(
        "body"
    ).inner_text()

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    results = []

    current_code = None
    current_rewards = []

    # Indique si le code actuel est réservé à l'Asie
    current_is_asia_only = False


    # ==================================================
    # SAUVEGARDE DU CODE ACTUEL
    # ==================================================

    def save_current():

        nonlocal current_code
        nonlocal current_rewards
        nonlocal current_is_asia_only

        if current_code is None:
            return

        # ----------------------------------------------
        # CODE ASIA UNIQUEMENT
        # ----------------------------------------------

        if current_is_asia_only:

            print(
                f"Code ignoré "
                f"(Asia server only) : "
                f"{current_code}"
            )

            return

        # ----------------------------------------------
        # CODE NORMAL
        # ----------------------------------------------

        results.append({
            "code": current_code,
            "rewards": current_rewards.copy()
        })


    # ==================================================
    # PARCOURS DE LA PAGE
    # ==================================================

    for line in lines:

        # ----------------------------------------------
        # NOUVEAU CODE
        # ----------------------------------------------

        if is_code(line):

            # Sauvegarde le précédent
            save_current()

            # Commence un nouveau code
            current_code = line
            current_rewards = []
            current_is_asia_only = False

            continue


        # ----------------------------------------------
        # ASIA SERVER ONLY
        # ----------------------------------------------

        if line.lower() == "asia server only":

            current_is_asia_only = True

            continue


        # ----------------------------------------------
        # LIGNES À IGNORER
        # ----------------------------------------------

        if line in STOP_LINES:
            continue


        # ----------------------------------------------
        # NAVIGATION DU SITE
        # ----------------------------------------------

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


        # ----------------------------------------------
        # EXPIRATION
        #
        # On la conserve car ton bot Discord
        # peut l'utiliser pour afficher :
        #
        # Expires in 1d 4h
        # ----------------------------------------------

        if line.lower().startswith("expires"):
            current_rewards.append(line)
            continue


        # ----------------------------------------------
        # VRAIE RÉCOMPENSE
        # ----------------------------------------------

        if current_code is not None:

            if is_reward(line):

                current_rewards.append(line)

            else:

                # Affichage utile pour vérifier
                # ce que le scraper ignore
                print(
                    f"Récompense ignorée : {line}"
                )


    # ==================================================
    # DERNIER CODE
    # ==================================================

    save_current()


    # ==================================================
    # SUPPRESSION DES DOUBLONS
    # ==================================================

    cleaned_results = []

    seen = set()

    for item in results:

        code = item["code"]

        if code in seen:
            continue

        seen.add(code)

        cleaned_results.append(item)


    return cleaned_results


# ==================================================
# SCRAPER GENSHIN + STAR RAIL
# ==================================================

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
                    f"ERREUR {game} : "
                    f"{error}"
                )

                results[game] = []


        browser.close()


    return results


# ==================================================
# TEST LOCAL
# ==================================================

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

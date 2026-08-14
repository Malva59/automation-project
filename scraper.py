from playwright.sync_api import sync_playwright
import re


GAMES = {
    "Genshin Impact":
        "https://www.crimsonwitch.com/codes/Genshin_Impact",

    "Honkai: Star Rail":
        "https://www.crimsonwitch.com/codes/Honkai_Star_Rail",
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
# NETTOYAGE D'UNE RÉCOMPENSE
# ==================================================

def clean_reward(text):

    text = text.strip()

    if not text:
        return None

    # ----------------------------------------------
    # Coming soon
    # ----------------------------------------------

    if text.lower() in {
        "coming soon",
        "coming soon!",
    }:
        return None

    # ----------------------------------------------
    # LIVESTREAM CODE
    # ----------------------------------------------

    if re.fullmatch(
        r"LIVESTREAM CODE\s*\d*",
        text,
        re.IGNORECASE
    ):
        return None

    # ----------------------------------------------
    # Roleplaying Games
    # ----------------------------------------------

    if "roleplaying" in text.lower():
        return None

    # ----------------------------------------------
    # On garde uniquement le nom de la récompense
    # jusqu'à sa quantité.
    #
    # Exemple :
    #
    # Traveler's Guide ×5 Primary & Secondary
    # Schooling (K-12)
    #
    # devient :
    #
    # Traveler's Guide ×5
    # ----------------------------------------------

    match = re.search(
        r"^(.+?(?:×|x)\s*\d+)",
        text,
        re.IGNORECASE
    )

    if match:
        return match.group(1).strip()

    return None


# ==================================================
# EXTRACTION D'UNE CARTE
# ==================================================

def extract_code_card(card):

    # ----------------------------------------------
    # CODE
    # ----------------------------------------------

    code_locator = card.locator(
        ".code-header .code"
    )

    if code_locator.count() == 0:
        return None

    code = code_locator.first.inner_text().strip()

    if not is_code(code):
        return None


    # ----------------------------------------------
    # ASIA SERVER ONLY
    # ----------------------------------------------

    card_text = card.inner_text()

    if "Asia server only" in card_text:
        print(
            f"Code ignoré (Asia server only) : {code}"
        )

        return None


    # ----------------------------------------------
    # EXPIRATION
    # ----------------------------------------------

    rewards = []

    time_locator = card.locator(
        ".code-header .time-left"
    )

    if time_locator.count() > 0:

        expiration = time_locator.first.inner_text().strip()

        if expiration:
            rewards.append(expiration)


    # ----------------------------------------------
    # RÉCOMPENSES
    # ----------------------------------------------

    reward_items = card.locator(
        "ul.rewards li.reward"
    )

    for i in range(reward_items.count()):

        reward_item = reward_items.nth(i)

        # ------------------------------------------
        # On cherche d'abord un <p>
        #
        # C'est important car le <li> peut contenir
        # d'autres informations comme :
        # Roleplaying Games
        # ------------------------------------------

        paragraph = reward_item.locator("p")

        if paragraph.count() > 0:

            reward_text = paragraph.first.inner_text().strip()

        else:

            reward_text = reward_item.inner_text().strip()


        # ------------------------------------------
        # Nettoyage
        # ------------------------------------------

        reward = clean_reward(reward_text)

        if not reward:
            continue


        # ------------------------------------------
        # Évite les doublons
        # ------------------------------------------

        if reward in rewards:
            continue

        rewards.append(reward)


    # ----------------------------------------------
    # RÉSULTAT
    # ----------------------------------------------

    return {
        "code": code,
        "rewards": rewards
    }


# ==================================================
# SCRAPER D'UN JEU
# ==================================================

def scrape_game_codes(page, url):

    print()
    print("=" * 60)
    print(f"Ouverture : {url}")
    print("=" * 60)


    # ----------------------------------------------
    # OUVERTURE
    # ----------------------------------------------

    page.goto(
        url,
        wait_until="networkidle",
        timeout=60000
    )

    page.wait_for_timeout(2000)


    # ----------------------------------------------
    # RÉCUPÉRATION DES CARTES
    # ----------------------------------------------

    cards = page.locator(
        "#codes .codes-wrapper .code-card"
    )

    card_count = cards.count()

    print(
        f"Cartes trouvées : {card_count}"
    )


    results = []

    seen = set()


    # ----------------------------------------------
    # PARCOURS DES CARTES
    # ----------------------------------------------

    for i in range(card_count):

        card = cards.nth(i)

        try:

            item = extract_code_card(card)

        except Exception as error:

            print(
                f"Erreur carte {i} : {error}"
            )

            continue


        if item is None:
            continue


        code = item["code"]


        # ------------------------------------------
        # DOUBLON
        # ------------------------------------------

        if code in seen:
            continue

        seen.add(code)


        # ------------------------------------------
        # AJOUT
        # ------------------------------------------

        results.append(item)


        # ------------------------------------------
        # LOG
        # ------------------------------------------

        print()
        print(f"CODE : {code}")

        print("RÉCOMPENSES :")

        for reward in item["rewards"]:

            print(
                f"  - {reward}"
            )


    print()
    print(
        f"{len(results)} codes récupérés"
    )


    return results


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


                print()
                print(
                    f"{game} : "
                    f"{len(codes)} codes trouvés"
                )


            except Exception as error:

                print()
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


    print()
    print("=" * 60)
    print("RÉSULTAT FINAL")
    print("=" * 60)


    for game, codes in results.items():

        print()
        print(
            f"===== {game} ====="
        )


        for item in codes:

            print()
            print(
                f"CODE : {item['code']}"
            )

            print(
                "RÉCOMPENSES :"
            )


            for reward in item["rewards"]:

                print(
                    f"  - {reward}"
                )

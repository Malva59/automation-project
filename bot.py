import os
import discord
import json
import subprocess
import time
from datetime import datetime, timezone, timedelta

from scraper import scrape_all_codes
from database import get_new_codes, mark_code_as_known


# ==================================================
# CONFIGURATION
# ==================================================

TOKEN = os.environ["DISCORD_TOKEN"]

CHANNEL_ID = int(
    os.environ.get(
        "DISCORD_CHANNEL_ID",
        "1494316922534367352"
    )
)

STATUS_FILE = "status.json"

# Recherche affichée au minimum 30 secondes
MIN_SEARCH_DISPLAY = 30

# Prochaine recherche prévue 5 minutes après
# le début du workflow
SEARCH_INTERVAL = 5 * 60


# ==================================================
# URLS D'ACTIVATION
# ==================================================

ACTIVATION_URLS = {

    "Genshin Impact":
        "https://genshin.hoyoverse.com/fr/gift?code=",

    "Honkai: Star Rail":
        "https://hsr.hoyoverse.com/gift?code=",

}


# ==================================================
# COULEURS DES EMBEDS
# ==================================================

EMBED_COLORS = {

    "Genshin Impact":
        0x8E7CC3,

    "Honkai: Star Rail":
        0x5B9BD5,

}


# ==================================================
# EMOJIS
# ==================================================

EMOJIS = {

    "Genshin Impact":
        "🎮",

    "Honkai: Star Rail":
        "🚂",

}


# ==================================================
# HEURE DU DÉBUT
# ==================================================

START_TIME = time.time()

STARTED_AT = datetime.now(
    timezone.utc
)

NEXT_SEARCH_AT = (
    STARTED_AT
    + timedelta(
        seconds=SEARCH_INTERVAL
    )
)


# ==================================================
# FORMAT DATE
# ==================================================

def iso_date(date):

    return date.strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


# ==================================================
# MISE À JOUR DU STATUS.JSON
# ==================================================

def update_status(
    status,
    completed_at=None
):

    data = {

        "status": status,

        "started_at":
            iso_date(STARTED_AT),

        "next_search_at":
            iso_date(NEXT_SEARCH_AT)

    }


    if completed_at is not None:

        data["completed_at"] = (
            iso_date(completed_at)
        )


    with open(
        STATUS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=2
        )


    print()
    print(
        "=========================================="
    )

    print(
        f"STATUS : {status}"
    )

    print(
        f"Début : {iso_date(STARTED_AT)}"
    )

    print(
        f"Prochaine recherche : "
        f"{iso_date(NEXT_SEARCH_AT)}"
    )

    if completed_at:

        print(
            f"Fin : {iso_date(completed_at)}"
        )

    print(
        "=========================================="
    )


# ==================================================
# SAUVEGARDER STATUS.JSON SUR GITHUB
# ==================================================

def push_status(message):

    try:

        subprocess.run(
            [
                "git",
                "add",
                STATUS_FILE
            ],
            check=True
        )


        result = subprocess.run(
            [
                "git",
                "diff",
                "--cached",
                "--quiet"
            ]
        )


        # Aucun changement
        if result.returncode == 0:

            print(
                "status.json déjà à jour."
            )

            return


        subprocess.run(
            [
                "git",
                "commit",
                "-m",
                message
            ],
            check=True
        )


        subprocess.run(
            [
                "git",
                "push",
                "origin",
                "main"
            ],
            check=True
        )


        print(
            "status.json envoyé sur GitHub."
        )


    except Exception as error:

        print(
            f"Erreur sauvegarde status.json : {error}"
        )

        raise


# ==================================================
# STATUT : RECHERCHE
# ==================================================

def start_search_status():

    update_status(
        "searching"
    )

    push_status(
        "Bot status: searching"
    )


# ==================================================
# STATUT : ATTENTE
# ==================================================

def finish_search_status():

    completed_at = datetime.now(
        timezone.utc
    )

    update_status(
        "waiting",
        completed_at
    )

    push_status(
        "Bot status: waiting"
    )


# ==================================================
# RECHERCHE DES CODES
# ==================================================

def get_codes_to_publish():

    print()
    print(
        "=========================================="
    )

    print(
        "🔎 Recherche des nouveaux codes..."
    )

    print(
        "=========================================="
    )


    all_codes = scrape_all_codes()


    codes_to_publish = {}


    for game, codes in all_codes.items():

        print()

        print(
            f"{game} : "
            f"{len(codes)} codes trouvés"
        )


        new_codes = get_new_codes(
            game,
            codes
        )


        print(
            f"{game} : "
            f"{len(new_codes)} nouveaux codes"
        )


        if new_codes:

            codes_to_publish[game] = (
                new_codes
            )


    return codes_to_publish


# ==================================================
# BOT DISCORD
# ==================================================

class GenshinBot(discord.Client):

    async def on_ready(self):

        print()
        print(
            f"Connecté en tant que {self.user}"
        )


        try:

            channel = await self.fetch_channel(
                CHANNEL_ID
            )


            print(
                f"Salon trouvé : #{channel.name}"
            )


            # ======================================
            # PUBLICATION DES CODES
            # ======================================

            for game, codes in (
                codes_to_publish.items()
            ):

                for item in codes:

                    code = item["code"]

                    rewards = item["rewards"]

                    emoji = EMOJIS[game]


                    activation_url = (
                        ACTIVATION_URLS[game]
                        + code
                    )


                    # ==================================
                    # EMBED
                    # ==================================

                    embed = discord.Embed(

                        title=(
                            f"{emoji} "
                            f"Nouveau code {game} !"
                        ),

                        description=(
                            "🎁 **Un nouveau code "
                            "vient d'être découvert !**"
                        ),

                        color=EMBED_COLORS[game]

                    )


                    # ==================================
                    # CODE
                    # ==================================

                    embed.add_field(

                        name="🎟️ Code",

                        value=f"```{code}```",

                        inline=False

                    )


                    # ==================================
                    # RÉCOMPENSES
                    # ==================================

                    if rewards:

                        rewards_text = "\n".join(

                            f"• {reward}"

                            for reward in rewards

                        )


                        embed.add_field(

                            name="🎁 Récompenses",

                            value=rewards_text[:1024],

                            inline=False

                        )

                    else:

                        embed.add_field(

                            name="🎁 Récompenses",

                            value="Non précisées",

                            inline=False

                        )


                    # ==================================
                    # FOOTER
                    # ==================================

                    embed.set_footer(

                        text=(
                            "Anteiku Hoyo codes • "
                            "Crimson Witch"
                        )

                    )


                    # ==================================
                    # BOUTON
                    # ==================================

                    view = discord.ui.View()


                    button = discord.ui.Button(

                        label="🎁 Utiliser le code",

                        style=discord.ButtonStyle.link,

                        url=activation_url

                    )


                    view.add_item(
                        button
                    )


                    # ==================================
                    # ENVOI
                    # ==================================

                    await channel.send(

                        embed=embed,

                        view=view

                    )


                    print(
                        f"Code publié ({game}) : "
                        f"{code}"
                    )


                    # ==================================
                    # MÉMORISATION
                    # ==================================

                    mark_code_as_known(

                        game,

                        code

                    )


            print()

            print(
                "Tous les nouveaux codes "
                "ont été traités."
            )


        except discord.NotFound:

            print(
                "ERREUR : salon Discord introuvable."
            )


        except discord.Forbidden:

            print(
                "ERREUR : le bot n'a pas "
                "les permissions nécessaires."
            )


        except discord.HTTPException as error:

            print(
                f"ERREUR Discord : {error}"
            )


        finally:

            # ==================================
            # FERMETURE DU BOT GITHUB
            # ==================================

            await self.close()

            print(
                "Connexion Discord fermée."
            )


# ==================================================
# MAIN
# ==================================================

try:

    # ==========================================
    # 1. STATUT RECHERCHE
    # ==========================================

    start_search_status()


    # ==========================================
    # 2. RECHERCHE
    # ==========================================

    codes_to_publish = (
        get_codes_to_publish()
    )


    # ==========================================
    # 3. ATTENDRE 30 SECONDES MINIMUM
    # ==========================================

    elapsed = (
        time.time()
        - START_TIME
    )


    if elapsed < MIN_SEARCH_DISPLAY:

        remaining = (
            MIN_SEARCH_DISPLAY
            - elapsed
        )


        print()

        print(
            f"Maintien du statut recherche "
            f"pendant {remaining:.1f} secondes..."
        )


        time.sleep(
            remaining
        )


    # ==========================================
    # 4. AUCUN NOUVEAU CODE
    # ==========================================

    if not codes_to_publish:

        print()

        print(
            "Aucun nouveau code à publier."
        )


    # ==========================================
    # 5. NOUVEAUX CODES
    # ==========================================

    else:

        total = sum(

            len(codes)

            for codes
            in codes_to_publish.values()

        )


        print()

        print(
            f"{total} code(s) à publier."
        )


        # ======================================
        # CONNEXION DISCORD
        # ======================================

        intents = discord.Intents.none()


        client = GenshinBot(
            intents=intents
        )


        client.run(
            TOKEN
        )


    # ==========================================
    # 6. STATUT ATTENTE
    # ==========================================

    finish_search_status()


except Exception as error:

    print()

    print(
        "=========================================="
    )

    print(
        f"ERREUR : {error}"
    )

    print(
        "=========================================="
    )


    # ==========================================
    # MÊME EN CAS D'ERREUR :
    # ON REMET LE STATUT À WAITING
    # ==========================================

    try:

        finish_search_status()

    except Exception as status_error:

        print(
            f"Impossible de mettre à jour "
            f"status.json : {status_error}"
        )


    raise

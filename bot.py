import os
import asyncio
import discord

from scraper import scrape_all_codes
from database import get_new_codes, mark_code_as_known


# ==================================================
# CONFIGURATION
# ==================================================

TOKEN = (
    os.getenv("DISCORD_TOKEN")
    or os.getenv("TOKEN")
    or os.getenv("BOT_TOKEN")
)

CHANNEL_ID = 1494316922534367352

# Rôle testé et fonctionnel
ROLE_ID = 1543027793695088640


# ==================================================
# LIENS D'ACTIVATION
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
    "Genshin Impact": 0x8E7CC3,
    "Honkai: Star Rail": 0x5B9BD5,
}


# ==================================================
# EMOJIS
# ==================================================

EMOJIS = {
    "Genshin Impact": "🎮",
    "Honkai: Star Rail": "🚂",
}


# ==================================================
# VÉRIFICATION DES CODES
# ==================================================

async def check_codes():

    print("========================================")
    print("Recherche des codes...")
    print("========================================")

    try:

        # Le scraper utilise Playwright.
        # On le lance dans un thread pour éviter
        # de bloquer la boucle asyncio de Discord.

        all_codes = await asyncio.to_thread(
            scrape_all_codes
        )

        codes_to_publish = {}

        # ==============================================
        # RECHERCHE DES NOUVEAUX CODES
        # ==============================================

        for game, codes in all_codes.items():

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
                codes_to_publish[game] = new_codes


        # ==============================================
        # AUCUN NOUVEAU CODE
        # ==============================================

        if not codes_to_publish:

            print("Aucun nouveau code.")

            return


        total = sum(
            len(codes)
            for codes in codes_to_publish.values()
        )

        print(
            f"{total} nouveau(x) code(s) à publier."
        )


        # ==============================================
        # RÉCUPÉRATION DU SALON DISCORD
        # ==============================================

        channel = await client.fetch_channel(
            CHANNEL_ID
        )

        print(
            f"Salon trouvé : #{channel.name}"
        )


        # ==============================================
        # PUBLICATION DES CODES
        # ==============================================

        for game, codes in codes_to_publish.items():

            for item in codes:

                code = item["code"]

                rewards = item.get(
                    "rewards",
                    []
                )

                emoji = EMOJIS.get(
                    game,
                    "🎁"
                )


                # ==========================================
                # LIEN D'ACTIVATION
                # ==========================================

                activation_url = (
                    ACTIVATION_URLS[game]
                    + code
                )


                # ==========================================
                # CRÉATION DE L'EMBED
                # ==========================================

                embed = discord.Embed(

                    title=(
                        f"{emoji} "
                        f"Nouveau code {game} !"
                    ),

                    description=(
                        "🎁 **Un nouveau code "
                        "vient d'être découvert !**"
                    ),

                    color=EMBED_COLORS.get(
                        game,
                        0x5865F2
                    )
                )


                # ==========================================
                # CODE
                # ==========================================

                embed.add_field(

                    name="🎟️ Code",

                    value=f"```{code}```",

                    inline=False
                )


                # ==========================================
                # RÉCOMPENSES
                # ==========================================

                if rewards:

                    rewards_text = "\n".join(
                        f"• {reward}"
                        for reward in rewards
                    )

                    # Limite Discord pour un champ d'embed
                    if len(rewards_text) > 1024:

                        rewards_text = (
                            rewards_text[:1021]
                            + "..."
                        )

                    embed.add_field(

                        name="🎁 Récompenses",

                        value=rewards_text,

                        inline=False
                    )

                else:

                    embed.add_field(

                        name="🎁 Récompenses",

                        value="Non précisées",

                        inline=False
                    )


                # ==========================================
                # FOOTER
                # ==========================================

                embed.set_footer(

                    text=(
                        "Anteiku Hoyo codes • "
                        "Malva"
                    )
                )


                # ==========================================
                # BOUTON D'ACTIVATION
                # ==========================================

                view = discord.ui.View(
                    timeout=None
                )

                button = discord.ui.Button(

                    label="🎁 Utiliser le code",

                    style=discord.ButtonStyle.link,

                    url=activation_url
                )

                view.add_item(button)


                # ==========================================
                # MENTION DU RÔLE
                # ==========================================

                role_mention = (
                    f"<@&{ROLE_ID}>"
                )

                allowed_mentions = (
                    discord.AllowedMentions(
                        roles=True
                    )
                )


                # ==========================================
                # ENVOI SUR DISCORD
                # ==========================================

                await channel.send(

                    content=role_mention,

                    embed=embed,

                    view=view,

                    allowed_mentions=allowed_mentions
                )


                print(
                    f"Code publié "
                    f"({game}) : {code}"
                )

                print(
                    f"Rôle pingé : {ROLE_ID}"
                )


                # ==========================================
                # SAUVEGARDE DU CODE
                # ==========================================

                mark_code_as_known(
                    game,
                    code
                )


        print(
            "Tous les nouveaux codes ont été traités."
        )


    except Exception as error:

        print(
            "ERREUR pendant la vérification :"
        )

        print(error)


# ==================================================
# BOT DISCORD
# ==================================================

class HoyoBot(discord.Client):

    async def setup_hook(self):

        # Rien à lancer ici.
        #
        # GitHub Actions doit effectuer UNE SEULE
        # vérification puis fermer le bot.

        pass


    async def on_ready(self):

        print("========================================")

        print(
            f"Connecté en tant que {self.user}"
        )

        print(
            "Recherche des codes..."
        )

        print("========================================")


        # ==============================================
        # UNE SEULE VÉRIFICATION
        # ==============================================

        await check_codes()


        # ==============================================
        # FERMETURE PROPRE
        # ==============================================

        print("========================================")

        print(
            "Vérification terminée."
        )

        print(
            "Fermeture du bot..."
        )

        print("========================================")


        await self.close()


# ==================================================
# VÉRIFICATION DU TOKEN
# ==================================================

if not TOKEN:

    raise RuntimeError(

        "TOKEN Discord introuvable. "

        "Vérifie le secret Discord "
        "dans GitHub."
    )


# ==================================================
# INTENTS
# ==================================================

intents = discord.Intents.none()


# ==================================================
# CRÉATION DU CLIENT
# ==================================================

client = HoyoBot(
    intents=intents
)


# ==================================================
# DÉMARRAGE
# ==================================================

client.run(TOKEN)

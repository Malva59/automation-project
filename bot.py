import os
import discord

from scraper import scrape_all_codes
from database import get_new_codes, mark_code_as_known


TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL_ID = int(os.environ["DISCORD_CHANNEL_ID"])


# Liens d'activation
ACTIVATION_URLS = {
    "Genshin Impact": "https://genshin.hoyoverse.com/fr/gift?code=",
    "Honkai: Star Rail": "https://hsr.hoyoverse.com/gift?code=",
}


# Couleurs des embeds
EMBED_COLORS = {
    "Genshin Impact": 0x8E7CC3,
    "Honkai: Star Rail": 0x5B9BD5,
}


# Emojis
EMOJIS = {
    "Genshin Impact": "🎮",
    "Honkai: Star Rail": "🚂",
}


def get_codes_to_publish():

    print("Recherche des codes...")

    all_codes = scrape_all_codes()

    codes_to_publish = {}

    for game, codes in all_codes.items():

        print(f"{game} : {len(codes)} codes trouvés")

        new_codes = get_new_codes(game, codes)

        print(
            f"{game} : {len(new_codes)} nouveaux codes"
        )

        if new_codes:
            codes_to_publish[game] = new_codes

    return codes_to_publish


class GenshinBot(discord.Client):

    async def on_ready(self):

        print(f"Connecté en tant que {self.user}")

        try:

            channel = await self.fetch_channel(CHANNEL_ID)

            print(f"Salon trouvé : #{channel.name}")

            for game, codes in codes_to_publish.items():

                for code in codes:

                    emoji = EMOJIS[game]

                    activation_url = (
                        ACTIVATION_URLS[game] + code
                    )

                    # Création de l'embed
                    embed = discord.Embed(
                        title=f"{emoji} Nouveau code {game} !",
                        description=(
                            "🎁 **Un nouveau code vient d'être découvert !**\n\n"
                            f"**Code :**\n"
                            f"```{code}```"
                        ),
                        color=EMBED_COLORS[game]
                    )

                    embed.set_footer(
                        text="Anteiku Hoyo codes • Crimson Witch"
                    )

                    # Bouton d'activation
                    view = discord.ui.View()

                    button = discord.ui.Button(
                        label="🎁 Utiliser le code",
                        style=discord.ButtonStyle.link,
                        url=activation_url
                    )

                    view.add_item(button)

                    # Envoi
                    await channel.send(
                        embed=embed,
                        view=view
                    )

                    print(
                        f"Code publié ({game}) : {code}"
                    )

                    # Le code est considéré comme connu
                    # uniquement après l'envoi réussi.
                    mark_code_as_known(
                        game,
                        code
                    )

            print(
                "Tous les nouveaux codes ont été traités."
            )

        except discord.NotFound:

            print(
                "ERREUR : salon Discord introuvable."
            )

        except discord.Forbidden:

            print(
                "ERREUR : le bot n'a pas la permission "
                "d'accéder ou d'écrire dans ce salon."
            )

        except discord.HTTPException as error:

            print(
                f"ERREUR Discord : {error}"
            )

        finally:

            await self.close()


# Recherche des codes avant de démarrer Discord
try:

    codes_to_publish = get_codes_to_publish()

except Exception as error:

    print(
        f"ERREUR pendant la recherche des codes : {error}"
    )

    raise


# Aucun nouveau code
if not codes_to_publish:

    print("Aucun nouveau code à publier.")
    print("Fin du workflow.")


# Nouveaux codes
else:

    total = sum(
        len(codes)
        for codes in codes_to_publish.values()
    )

    print(
        f"{total} code(s) à publier."
    )

    intents = discord.Intents.none()

    client = GenshinBot(
        intents=intents
    )

    client.run(TOKEN)

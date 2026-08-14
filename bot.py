import os
import discord

from scraper import scrape_genshin_codes
from database import get_new_codes, mark_code_as_known


TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL_ID = int(os.environ["DISCORD_CHANNEL_ID"])


def get_codes_to_publish():
    print("Recherche des codes Genshin...")

    codes = scrape_genshin_codes()

    print(f"Codes trouvés : {len(codes)}")

    new_codes = get_new_codes(codes)

    print(f"Nouveaux codes : {len(new_codes)}")

    return new_codes


class GenshinBot(discord.Client):

    async def on_ready(self):
        print(f"Connecté en tant que {self.user}")

        try:
            channel = await self.fetch_channel(CHANNEL_ID)

            print(f"Salon trouvé : #{channel.name}")

            for code in new_codes:

                message = (
                    "🎁 **Nouveau code Genshin Impact !**\n\n"
                    f"```{code}```\n"
                    "🎮 Pense à l'utiliser rapidement !"
                )

                await channel.send(message)

                print(f"Code publié : {code}")

                # Le code est marqué comme connu uniquement
                # après l'envoi réussi sur Discord.
                mark_code_as_known(code)

            print("Tous les nouveaux codes ont été publiés.")

        except discord.NotFound:
            print("ERREUR : salon Discord introuvable.")

        except discord.Forbidden:
            print(
                "ERREUR : le bot n'a pas la permission "
                "d'accéder ou d'écrire dans ce salon."
            )

        except discord.HTTPException as error:
            print(f"ERREUR Discord : {error}")

        finally:
            await self.close()


# --------------------------------------------------
# Recherche des codes AVANT de démarrer Discord.
# Cela évite de mélanger Playwright Sync et asyncio.
# --------------------------------------------------

try:
    new_codes = get_codes_to_publish()

except Exception as error:
    print(f"ERREUR pendant la recherche des codes : {error}")
    raise


# S'il n'y a aucun nouveau code, inutile de connecter
# le bot à Discord.
if not new_codes:

    print("Aucun nouveau code à publier.")
    print("Fin du workflow.")

else:

    print(f"{len(new_codes)} code(s) à publier.")

    intents = discord.Intents.none()

    client = GenshinBot(intents=intents)

    client.run(TOKEN)

import os
import discord

from scraper import scrape_genshin_codes
from database import get_new_codes, mark_code_as_known


TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL_ID = int(os.environ["DISCORD_CHANNEL_ID"])


class GenshinBot(discord.Client):
    async def on_ready(self):
        print(f"Connecté en tant que {self.user}")

        try:
            # Récupération des codes depuis Crimson Witch
            codes = scrape_genshin_codes()

            print(f"Codes trouvés : {len(codes)}")

            # Comparaison avec les codes déjà publiés
            new_codes = get_new_codes(codes)

            print(f"Nouveaux codes : {len(new_codes)}")

            if not new_codes:
                print("Aucun nouveau code.")
                await self.close()
                return

            # Récupération du salon Discord
            channel = await self.fetch_channel(CHANNEL_ID)

            print(f"Salon trouvé : #{channel.name}")

            # Publication des nouveaux codes
            for code in new_codes:
                message = (
                    "🎁 **Nouveau code Genshin Impact !**\n\n"
                    f"```{code}```\n"
                    "🎮 Pense à l'utiliser rapidement !"
                )

                await channel.send(message)

                print(f"Code publié : {code}")

                # On ne considère le code comme connu
                # qu'après son envoi réussi
                mark_code_as_known(code)

            print("Tous les nouveaux codes ont été publiés.")

        except discord.NotFound:
            print("ERREUR : salon Discord introuvable.")

        except discord.Forbidden:
            print(
                "ERREUR : le bot n'a pas la permission "
                "d'écrire dans ce salon."
            )

        except discord.HTTPException as error:
            print(f"ERREUR Discord : {error}")

        except Exception as error:
            print(f"ERREUR : {error}")

        finally:
            await self.close()


intents = discord.Intents.none()

client = GenshinBot(intents=intents)

client.run(TOKEN)

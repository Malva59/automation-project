import os
import discord

TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL_ID = int(os.environ["DISCORD_CHANNEL_ID"])


class TestBot(discord.Client):
    async def on_ready(self):
        print(f"Connecté en tant que {self.user}")

        try:
            channel = await self.fetch_channel(CHANNEL_ID)

            print(f"Salon trouvé : #{channel.name}")
            print(f"Serveur : {channel.guild.name}")

            await channel.send("🤖 Connexion du bot réussie !")
            print("Message envoyé avec succès.")

        except discord.NotFound:
            print("ERREUR : salon introuvable ou inaccessible.")

        except discord.Forbidden:
            print("ERREUR : le bot n'a pas la permission d'accéder ou d'écrire dans ce salon.")

        except discord.HTTPException as error:
            print(f"ERREUR Discord : {error}")

        finally:
            await self.close()


intents = discord.Intents.none()

client = TestBot(intents=intents)
client.run(TOKEN)

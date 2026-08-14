import os
import discord

TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL_ID = int(os.environ["DISCORD_CHANNEL_ID"])


class TestBot(discord.Client):
    async def on_ready(self):
        print(f"Connecté en tant que {self.user}")

        channel = self.get_channel(CHANNEL_ID)

        if channel is None:
            print("ERREUR : salon introuvable.")
            await self.close()
            return

        await channel.send("🤖 Connexion du bot réussie !")
        print("Message envoyé avec succès.")

        await self.close()


intents = discord.Intents.none()

client = TestBot(intents=intents)
client.run(TOKEN)

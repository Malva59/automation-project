import os
import asyncio
import discord
import json
import urllib.request
import time
from datetime import datetime, timezone


# ==========================================
# TOKEN DISCORD
# ==========================================

TOKEN = (
    os.getenv("TOKEN")
    or os.getenv("DISCORD_TOKEN")
    or os.getenv("BOT_TOKEN")
    or os.getenv("TOKEN_DU_BOT")
)


# ==========================================
# CONFIGURATION
# ==========================================

STATUS_URL = (
    "https://raw.githubusercontent.com/"
    "Malva59/automation-project/main/status.json"
)

CHECK_INTERVAL = 5

MAX_SEARCH_DISPLAY = 30


# ==========================================
# VÉRIFICATION DU TOKEN
# ==========================================

if not TOKEN:
    raise RuntimeError(
        "TOKEN Discord introuvable. "
        "Vérifie le champ TOKEN DU BOT dans Startup."
    )


# ==========================================
# INTENTS
# ==========================================

intents = discord.Intents.none()


# ==========================================
# RÉCUPÉRATION DU STATUS
# ==========================================

def get_status():

    try:

        url = (
            STATUS_URL
            + "?cache="
            + str(time.time())
        )

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Anteiku-Hoyo-Bot/1.0",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache"
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=10
        ) as response:

            return json.loads(
                response.read().decode("utf-8")
            )

    except Exception as error:

        print(
            f"[GitHub] Erreur : {error}"
        )

        return None


# ==========================================
# CONVERSION DATE
# ==========================================

def parse_date(value):

    if not value:
        return None

    try:

        return datetime.fromisoformat(
            value.replace(
                "Z",
                "+00:00"
            )
        )

    except Exception:

        return None


# ==========================================
# BOT
# ==========================================

class HoyoBot(discord.Client):

    async def on_ready(self):

        print("========================================")
        print(
            f"Connecté en tant que {self.user}"
        )
        print("Bot H24 en ligne.")
        print("Surveillance de status.json.")
        print("========================================")

        await self.change_presence(
            activity=discord.Game(
                name="⏱️ Prochaine recherche..."
            )
        )

        self.loop.create_task(
            monitor_status()
        )


# ==========================================
# SURVEILLANCE
# ==========================================

async def monitor_status():

    await client.wait_until_ready()

    search_started_at = None
    last_status = None
    last_display = None

    while not client.is_closed():

        try:

            data = await asyncio.to_thread(
                get_status
            )

            if data:

                status = data.get(
                    "status"
                )

                next_search_at = data.get(
                    "next_search_at"
                )

                print(
                    f"[GitHub] status={status} "
                    f"| next_search_at={next_search_at}"
                )


                # ==================================
                # RECHERCHE
                # ==================================

                if status == "searching":

                    if last_status != "searching":

                        search_started_at = time.time()

                        print(
                            "[Discord] 🔎 Recherche de nouveaux codes..."
                        )


                    elapsed = (
                        time.time()
                        - search_started_at
                    )


                    if elapsed < MAX_SEARCH_DISPLAY:

                        display = (
                            "🔎 Recherche de nouveaux codes..."
                        )

                    else:

                        display = (
                            "⏱️ Prochaine recherche..."
                        )


                    if display != last_display:

                        await client.change_presence(
                            activity=discord.Game(
                                name=display
                            )
                        )

                        print(
                            f"[Discord] {display}"
                        )

                        last_display = display


                    last_status = "searching"


                # ==================================
                # ATTENTE
                # ==================================

                elif status == "waiting":

                    search_started_at = None

                    next_search = parse_date(
                        next_search_at
                    )


                    if next_search:

                        now = datetime.now(
                            timezone.utc
                        )

                        remaining = (
                            next_search - now
                        ).total_seconds()


                        if remaining > 0:

                            minutes = int(
                                (remaining + 59) // 60
                            )

                            display = (
                                f"⏱️ Prochaine recherche "
                                f"dans {minutes} min"
                            )

                        else:

                            display = (
                                "⏱️ Prochaine recherche..."
                            )

                    else:

                        display = (
                            "⏱️ Prochaine recherche..."
                        )


                    if display != last_display:

                        await client.change_presence(
                            activity=discord.Game(
                                name=display
                            )
                        )

                        print(
                            f"[Discord] {display}"
                        )

                        last_display = display


                    last_status = "waiting"


                # ==================================
                # INCONNU
                # ==================================

                else:

                    display = (
                        "⏱️ Prochaine recherche..."
                    )

                    if display != last_display:

                        await client.change_presence(
                            activity=discord.Game(
                                name=display
                            )
                        )

                        print(
                            f"[Discord] {display}"
                        )

                        last_display = display


        except Exception as error:

            print(
                f"[Status] Erreur : {error}"
            )


        await asyncio.sleep(
            CHECK_INTERVAL
        )


# ==========================================
# CLIENT
# ==========================================

client = HoyoBot(
    intents=intents
)


# ==========================================
# DÉMARRAGE
# ==========================================

client.run(TOKEN)

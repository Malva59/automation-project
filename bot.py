import os
import asyncio
import json
import urllib.request
import discord
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
# CONFIGURATION GITHUB
# ==========================================

GITHUB_OWNER = "Malva59"
GITHUB_REPO = "automation-project"

# Vérification de l'état GitHub toutes les 60 secondes
CHECK_INTERVAL = 60

# Le Cron Job lance une recherche toutes les 5 minutes
SEARCH_INTERVAL = 5


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
# FONCTIONS GITHUB
# ==========================================

def get_latest_workflow():

    url = (
        f"https://api.github.com/repos/"
        f"{GITHUB_OWNER}/{GITHUB_REPO}/actions/runs"
        f"?per_page=1"
    )

    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "Anteiku-Hoyo-Bot"
        }
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=10
        ) as response:

            data = json.loads(
                response.read().decode("utf-8")
            )

        runs = data.get("workflow_runs", [])

        if not runs:
            return None

        return runs[0]

    except Exception as error:

        print(
            f"Erreur GitHub API : {error}"
        )

        return None


# ==========================================
# CALCUL DU TEMPS
# ==========================================

def get_minutes_remaining(completed_at):

    if not completed_at:
        return SEARCH_INTERVAL

    try:

        completed_time = datetime.fromisoformat(
            completed_at.replace("Z", "+00:00")
        )

        next_search = (
            completed_time.timestamp()
            + SEARCH_INTERVAL * 60
        )

        now = datetime.now(
            timezone.utc
        ).timestamp()

        remaining = next_search - now

        if remaining <= 0:
            return 0

        # Arrondi vers le haut
        return int(
            (remaining + 59) // 60
        )

    except Exception:

        return SEARCH_INTERVAL


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
        print("GitHub Actions s'occupe des codes.")
        print("========================================")

        # Lance la surveillance GitHub
        self.loop.create_task(
            self.update_status()
        )


    # ======================================
    # STATUT DISCORD
    # ======================================

    async def update_status(self):

        await self.wait_until_ready()

        while not self.is_closed():

            try:

                latest_run = await asyncio.to_thread(
                    get_latest_workflow
                )


                # ==================================
                # AUCUN WORKFLOW TROUVÉ
                # ==================================

                if latest_run is None:

                    await self.change_presence(
                        activity=discord.Game(
                            name="⏱️ Prochaine recherche dans 5 min"
                        )
                    )


                else:

                    status = latest_run.get(
                        "status"
                    )


                    # ==================================
                    # RECHERCHE EN COURS
                    # ==================================

                    if status in {
                        "queued",
                        "in_progress"
                    }:

                        print(
                            "GitHub Actions : "
                            "recherche en cours."
                        )

                        await self.change_presence(
                            activity=discord.Game(
                                name="🔎 Recherche de nouveaux codes..."
                            )
                        )


                    # ==================================
                    # RECHERCHE TERMINÉE
                    # ==================================

                    else:

                        completed_at = latest_run.get(
                            "updated_at"
                        )

                        minutes = get_minutes_remaining(
                            completed_at
                        )


                        # Si la prochaine recherche
                        # est imminente
                        if minutes <= 0:

                            await self.change_presence(
                                activity=discord.Game(
                                    name="🔎 Recherche de nouveaux codes..."
                                )
                            )

                        else:

                            await self.change_presence(
                                activity=discord.Game(
                                    name=(
                                        f"⏱️ Prochaine recherche "
                                        f"dans {minutes} min"
                                    )
                                )
                            )


            except Exception as error:

                print(
                    f"Erreur statut : {error}"
                )


            # Vérification toutes les minutes
            await asyncio.sleep(
                CHECK_INTERVAL
            )


# ==========================================
# CRÉATION DU BOT
# ==========================================

client = HoyoBot(
    intents=intents
)


# ==========================================
# DÉMARRAGE
# ==========================================

client.run(TOKEN)

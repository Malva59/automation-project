import os
import asyncio
import discord
import json
import urllib.request
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

GITHUB_OWNER = "Malva59"
GITHUB_REPO = "automation-project"

# GitHub est vérifié toutes les 30 secondes
CHECK_INTERVAL = 30

# Ton Cron Job lance une recherche toutes les 5 minutes
SEARCH_INTERVAL = 5 * 60


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
# GITHUB
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

        runs = data.get(
            "workflow_runs",
            []
        )

        if not runs:
            return None

        return runs[0]

    except Exception as error:

        print(
            f"Erreur GitHub API : {error}"
        )

        return None


# ==========================================
# CONVERSION DATE
# ==========================================

def parse_github_date(date_string):

    if not date_string:
        return None

    try:

        return datetime.fromisoformat(
            date_string.replace(
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
        print("Surveillance de GitHub Actions.")
        print("========================================")

        # Statut initial
        await self.change_presence(
            activity=discord.Game(
                name="⏱️ Prochaine recherche dans 5 min"
            )
        )

        # Lance la surveillance
        self.loop.create_task(
            monitor_github()
        )


# ==========================================
# SURVEILLANCE GITHUB
# ==========================================

async def monitor_github():

    await client.wait_until_ready()

    last_run_id = None

    while not client.is_closed():

        try:

            workflow = await asyncio.to_thread(
                get_latest_workflow
            )


            if workflow is None:

                await asyncio.sleep(
                    CHECK_INTERVAL
                )

                continue


            run_id = workflow.get(
                "id"
            )

            status = workflow.get(
                "status"
            )

            conclusion = workflow.get(
                "conclusion"
            )


            # ==================================
            # NOUVEAU WORKFLOW
            # ==================================

            if run_id != last_run_id:

                last_run_id = run_id

                print(
                    f"Nouveau workflow détecté : {run_id}"
                )


            # ==================================
            # WORKFLOW EN COURS
            # ==================================

            if status in {
                "queued",
                "in_progress"
            }:

                print(
                    "GitHub Actions : recherche en cours."
                )

                await client.change_presence(
                    activity=discord.Game(
                        name="🔎 Recherche de nouveaux codes..."
                    )
                )


            # ==================================
            # WORKFLOW TERMINÉ
            # ==================================

            else:

                completed_at = parse_github_date(
                    workflow.get(
                        "updated_at"
                    )
                )

                if completed_at is None:

                    await client.change_presence(
                        activity=discord.Game(
                            name="⏱️ Prochaine recherche dans 5 min"
                        )
                    )

                else:

                    next_search = (
                        completed_at.timestamp()
                        + SEARCH_INTERVAL
                    )

                    now = datetime.now(
                        timezone.utc
                    ).timestamp()

                    remaining = (
                        next_search - now
                    )


                    # ==================================
                    # PROCHAINE RECHERCHE IMMINENTE
                    # ==================================

                    if remaining <= 0:

                        await client.change_presence(
                            activity=discord.Game(
                                name="🔎 Recherche de nouveaux codes..."
                            )
                        )


                    else:

                        minutes = int(
                            (remaining + 59) // 60
                        )

                        await client.change_presence(
                            activity=discord.Game(
                                name=(
                                    f"⏱️ Prochaine recherche "
                                    f"dans {minutes} min"
                                )
                            )
                        )


        except Exception as error:

            print(
                f"Erreur surveillance GitHub : {error}"
            )


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

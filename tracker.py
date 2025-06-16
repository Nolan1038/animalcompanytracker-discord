import discord
from discord.ext import tasks, commands
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
from keep_alive import keep_alive


TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
ROLE_ID = int(os.getenv("DISCORD_ROLE_ID"))  # Use the actual ID of the @Update Pings role

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

META_URL = "https://www.meta.com/en-gb/experiences/animal-company/7190422614401072/"
last_logged_version = None  # Will update in memory, or persist to a file if needed

def fetch_version():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(META_URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    version_spans = soup.find_all("span")

    for span in version_spans:
        if span.text.strip().lower().startswith("version"):
            return span.text.strip().split(" ")[-1]  # Extract version number
    return None

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    check_version.start()

@tasks.loop(hours=1)
async def check_version():
    global last_logged_version

    current_version = fetch_version()
    if not current_version:
        print("Could not fetch version.")
        return

    if current_version != last_logged_version:
        print(f"New version detected: {current_version}")
        channel = bot.get_channel(CHANNEL_ID)
        embed = discord.Embed(title="ReTracker v1", description="**Update Detected!**", color=0x5865F2)
        embed.add_field(name="\U0001F7E2 | Updated Version:", value=current_version, inline=True)
        embed.add_field(name="\U0001F534 | Last Logged:", value=last_logged_version or "None", inline=True)
        embed.set_image(url="https://cdn.cloudflare.steamstatic.com/steam/apps/2292040/header.jpg")
        embed.timestamp = datetime.utcnow()

        await channel.send(content=f"<@&{ROLE_ID}>", embed=embed)
        last_logged_version = current_version
    else:
        print("No update found.")

keep_alive()
bot.run(TOKEN)

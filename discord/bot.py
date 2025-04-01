import discord
from discord.ext import commands
from discord.ui import Button, View
import requests
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
exchange_url = "http://endpoint/api"  # replacing this with dr. cat exchange endpoint
def fetch_exchange_data():
    try:
        response = requests.get(exchange_url)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Failed to fetch data."}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
class APIButtonView(View):
    @discord.ui.button(label="Fetch API Info", style=discord.ButtonStyle.primary)
    async def fetch_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = fetch_exchange_data()
        if 'error' in data:
            await interaction.response.send_message(f"Error: {data['error']}")
        else:
            await interaction.response.send_message(f"API Response: {data}")
@bot.command()
async def start(ctx):
    view = APIButtonView()
    await ctx.send("Click the button to fetch API info:", view=view)
bot.run(' ') # put the bot token here

import discord
from discord.ext import commands
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
TALER_API_KEY = os.getenv("TALER_API_KEY")
TALER_MERCHANT_URL = os.getenv("TALER_MERCHANT_URL", "http://localhost:9966")

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!escrow ", intents=intents)

# Taler API interaction functions
def create_taler_order(amount, description):
    headers = {"Authorization": f"Bearer {TALER_API_KEY}"}
    payload = {
        "amount": f"USD:{amount}",
        "summary": description,
        "fulfillment_url": "http://example.com/fulfill"  # Placeholder - using a drcat.fun service for Taler Exchange.
    }
    response = requests.post(f"{TALER_MERCHANT_URL}/order", json=payload, headers=headers)
    return response.json() if response.status_code == 200 else None

def check_payment_status(order_id):
    headers = {"Authorization": f"Bearer {TALER_API_KEY}"}
    response = requests.get(f"{TALER_MERCHANT_URL}/order/{order_id}", headers=headers)
    return response.json() if response.status_code == 200 else None

def release_funds(order_id):
    headers = {"Authorization": f"Bearer {TALER_API_KEY}"}
    response = requests.post(f"{TALER_MERCHANT_URL}/order/{order_id}/pay", headers=headers)
    return response.status_code == 200

def refund_funds(order_id):
    headers = {"Authorization": f"Bearer {TALER_API_KEY}"}
    response = requests.post(f"{TALER_MERCHANT_URL}/order/{order_id}/refund", headers=headers)
    return response.status_code == 200

# Bot events and commands
@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")

@bot.command(name="start")
async def start_escrow(ctx, amount: float, recipient: discord.User, *, description):
    """Start an escrow transaction. Usage: !escrow start <amount> @user <description>"""
    order = create_taler_order(amount, description)
    if not order:
        await ctx.send("Failed to create escrow order with GNU Taler.")
        return

    order_id = order["order_id"]
    payment_url = order["taler_pay_uri"]  # URL for buyer to pay

    await ctx.send(
        f"Escrow started!\n"
        f"Amount: {amount} EUR\n"
        f"Recipient: {recipient.mention}\n"
        f"Description: {description}\n"
        f"Buyer, please pay here: {payment_url}\n"
        f"Order ID: {order_id}"
    )
    # Store order_id in a database or dict for simplicity (e.g., {order_id: {"buyer": ctx.author.id, "recipient": recipient.id}})

@bot.command(name="release")
async def release_escrow(ctx, order_id: str):
    """Release funds to the recipient. Usage: !escrow release <order_id>"""
    status = check_payment_status(order_id)
    if not status or not status.get("paid"):
        await ctx.send("Payment not completed or order not found.")
        return

    if release_funds(order_id):
        await ctx.send(f"Funds released for order {order_id}!")
    else:
        await ctx.send("Failed to release funds.")

@bot.command(name="refund")
async def refund_escrow(ctx, order_id: str):
    """Refund funds to the buyer. Usage: !escrow refund <order_id>"""
    if refund_funds(order_id):
        await ctx.send(f"Funds refunded for order {order_id}!")
    else:
        await ctx.send("Failed to refund funds.")

# Run the bot
bot.run(TOKEN)

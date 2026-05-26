import os
import aiohttp
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, ContextTypes

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

COINS = {
    "BTC": "bitcoin",
    "TON": "the-open-network",
    "SOL": "solana",
}

async def get_prices():
    ids = ",".join(COINS.values())
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": ids, "vs_currencies": "usd"}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, timeout=10) as resp:
            resp.raise_for_status()
            data = await resp.json()

    return "\n".join(
        f"{symbol}: ${data[coin_id]['usd']:,.2f}"
        for symbol, coin_id in COINS.items()
    )

async def send_prices(context: ContextTypes.DEFAULT_TYPE):
    try:
        text = "💰 Crypto prices:\n\n" + await get_prices()
        await context.bot.send_message(chat_id=CHAT_ID, text=text)
    except Exception as e:
        await context.bot.send_message(chat_id=CHAT_ID, text=f"Ошибка: {e}")

async def start(update, context):
    await update.message.reply_text("Бот запущен. Цены будут приходить каждую минуту.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.job_queue.run_repeating(
        send_prices,
        interval=60,
        first=5,
    )

    app.run_polling()

if __name__ == "__main__":
    main()

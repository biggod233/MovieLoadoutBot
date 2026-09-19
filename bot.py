import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route
import uvicorn

# 1. YOUR TOKEN
# On Render, this will be pulled from an Environment Variable for security.
# For local testing, you can temporarily paste it here between the quotes, but REMOVE it before pushing to GitHub!
TOKEN = os.environ.get("BOT_TOKEN")

# 2. YOUR MOVIE DATABASE
MOVIE_DATABASE = {
    "inception": "https://example.com/inception-download-link",
    "avatar": "https://example.com/avatar-download-link",
    "the matrix": "https://example.com/matrix-download-link"
}

# 3. START COMMAND
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="Hello! I am the MovieLoadout bot. Send me a movie title to search!"
    )

# 4. SEARCH FUNCTION
async def search_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_query = update.message.text.lower().strip()
    
    if user_query in MOVIE_DATABASE:
        movie_link = MOVIE_DATABASE[user_query]
        reply_text = f"🎬 Found it! Here is the link for {user_query.title()}:\n{movie_link}"
    else:
        reply_text = f"❌ Sorry, I couldn't find {user_query.title()} in my database."

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=reply_text,
        parse_mode='Markdown'
    )

# 5. SET UP THE BOT APPLICATION
application = ApplicationBuilder().token(TOKEN).build()
start_handler = CommandHandler('start', start)
movie_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), search_movie)
application.add_handler(start_handler)
application.add_handler(movie_handler)

# 6. WEBHOOK LOGIC (The new part that talks to Render)
async def telegram_webhook(request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return PlainTextResponse("ok")

async def health(request):
    return PlainTextResponse("OK")

routes = [
    Route("/webhook", telegram_webhook, methods=["POST"]),
    Route("/", health, methods=["GET"])
]
app = Starlette(routes=routes)

import asyncio

async def main():
    # Initialize the bot application before starting the web server
    await application.initialize()
    await application.start()
    
    # Start the web server
    config = uvicorn.Config(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())

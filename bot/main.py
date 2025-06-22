import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler, Updater, \
	CallbackContext, ContextTypes, filters

from bot.ai_core import analyze_sentiment

# Загружаем переменные из .env
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

# Обработчик команды /start
async def start(update: Update, context:ContextTypes.DEFAULT_TYPE) -> None:
	await update.message.reply_text("Привет! Я твой ИИ-помощник 🤖")

# Новый обработчик: анализ любого текста
async def analyze(update:Update, context:ContextTypes.DEFAULT_TYPE) -> None:
	user_text = update.message.text
	responce = analyze_sentiment(user_text)
	await update.message.reply_text(responce)

#точка входа
if __name__ == '__main__':
	app = ApplicationBuilder().token(TOKEN).build()

	# Регистрируем команду /start
	app.add_handler(CommandHandler('start', start))

	app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, analyze))
	print('Бот запущен...')
	app.run_polling()
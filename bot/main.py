#main.py
import os
import matplotlib.pyplot  as plt
import io
import aiosqlite

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile

from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler, Updater, \
	CallbackContext, ContextTypes, filters, CallbackQueryHandler

from bot.ai_core import analyze_sentiment
from bot.database import init_db, save_result, DB_NAME, get_last_records, get_sentiment_stats

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Загружаем переменные из .env
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

#Функция, вызываемая после инициализации бота
async def post_init(application):
	await init_db()
	print("База данных инициализированна")
	await show_data()

# Отображение SQLite таблицы в консоле
async def show_data():
	async with aiosqlite.connect(DB_NAME) as db:
		cursor = await db.execute("SELECT * FROM emotions")
		rows = await cursor.fetchall()
		print("\nСодержимое таблицы emotions:")
		for row in rows:
			print(row)
		print()

# Обработчик команды /start
async def start(update: Update, context:ContextTypes.DEFAULT_TYPE) -> None:
	await update.message.reply_text("Привет! Я твой ИИ-помощник 🤖")

# Новый обработчик: анализ любого текста
async def analyze(update:Update, context:ContextTypes.DEFAULT_TYPE) -> None:
	user_text = update.message.text
	context.user_data['last_message'] = user_text
	responce = await analyze_sentiment(user_text)

	# Сохраняем ВСЕ сообщения автоматически
	success = await save_result(
		user_id=update.effective_user.id,
		message=user_text,
		sentiment=responce,
		lang= 'ru' if 'RU' in responce else 'en'
	)
	if not success:
		print('⚠️Не удалось сохранить сообщение')
	await update.message.reply_text(responce)

# Кнопка "Проверить эмоцию"
async def ask_emotion_check(update:Update, context:ContextTypes.DEFAULT_TYPE) -> None:
	keyboard = [
		[InlineKeyboardButton('Проверить эмоцию', callback_data='analyze_emotion')],
	]
	reply_markup = InlineKeyboardMarkup(keyboard)
	await update.message.reply_text(text = f'Анализирую: {update.message.text}', reply_markup=reply_markup)

# Обработка callback-кнопки
async def button_handler(update:Update, context:ContextTypes.DEFAULT_TYPE) -> None:
	query = update.callback_query
	await query.answer()

	last_record = await get_last_records(query.from_user.id)
	if last_record:
		await query.edit_message_text(text = f'Последний анализ: \n{last_record[3]}')
	else:
		await query.edit_message_text(text = 'Нет данных для отображения')

#Проверка БД в telegram
async def show_data_command(update:Update, context:ContextTypes.DEFAULT_TYPE) -> None:
	await show_data()
	await update.message.reply_text('Данные выведены в консоль сервера')

# Команда /history — показать последние записи
async def history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	user_id = update.effective_user.id
	records = await get_last_records(user_id)

	if not records:
		await update.message.reply_text('История пуста.')
		return

	response = "🕓 Последние записи:\n\n"
	for i, (msg, sentiment, timestamp) in enumerate(records, start=1):
		response += f'{i}, {timestamp[:19]} \n 🗣️ {msg}\n📊 {sentiment}\n\n'

	await update.message.reply_text(response)

# Команда /stats — текст + график
async def stats(update:Update, context:ContextTypes.DEFAULT_TYPE) -> None:
	user_id = update.effective_user.id
	stats = await get_sentiment_stats(user_id)

	total = sum(stats.values())
	if total == 0:
		await update.message.reply_text("Нет данных для статистики.")
		return

	message = f"📊 Ваша статистика по эмоциям:\n\n"
	message += f"😊 Позитивных: {stats['позитивная']}\n"
	message += f"😐 Нейтральных: {stats['нейтральная']}\n"
	message += f"😞 Негативных: {stats['негативная']}\n"
	message += f"\nВсего сообщений: {total}"

	await update.message.reply_text(message)

	labels, sizes, colors = [], [], []

	if stats ['позитивная'] >0:
		labels.append('позитивная')
		sizes.append(stats['позитивная'])
		colors.append('#66bb6a')

	if stats['нейтральная'] > 0:
		labels.append('нейтральная')
		sizes.append(stats['нейтральная'])
		colors.append('#ffa726')  # оранжевый

	if stats['негативная'] > 0:
		labels.append('негативная')
		sizes.append(stats['негативная'])
		colors.append('#ef5350')  # красный

	fig, ax = plt.subplots()
	ax.pie(sizes, colors=colors, labels=labels, autopct='%1.1f%%', startangle=90)
	ax.axis('equal')

	buffer = io.BytesIO()
	plt.savefig(buffer, format = 'png')
	buffer.seek(0)

	await update.message.reply_photo(photo=InputFile(buffer, filename  = 'stats.png'))
	buffer.close()
	plt.close()

#точка входа
if __name__ == '__main__':
	try:
		#asyncio.run(init_db())
		app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()
		#app = ApplicationBuilder().token(TOKEN).build()

		# Регистрируем команду /start
		app.add_handler(CommandHandler('start', start))
		app.add_handler(CommandHandler('check', ask_emotion_check))
		app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, analyze))
		app.add_handler(CallbackQueryHandler(button_handler))
		app.add_handler(CommandHandler('show_data', show_data_command))
		app.add_handler(CommandHandler('analyze', analyze))
		app.add_handler(CommandHandler('history', history))
		app.add_handler(CommandHandler('stats', stats))

		print('Бот запущен...')
		app.run_polling()
	except Exception as e:
		print(f"Бот упал с ошибкой: {e}")


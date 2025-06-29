from datetime import datetime
import os
import aiosqlite

DB_NAME = os.path.join(os.path.dirname(__file__), 'data.db')

# Создание таблицы, если её нет
async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS emotions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT,
            sentiment TEXT,
            lang TEXT, 
            timestamp TEXT
        )
        """)
        await db.commit()

# Сохраняем результат анализа
async def save_result(user_id: int, message:str, sentiment:str, lang:str):
    print(f"Пытаюсь сохранить в {os.path.abspath(DB_NAME)}")  # Логируем путь
    try:
        async with aiosqlite.connect(DB_NAME) as db:
            # Включаем журналирование для отладки
            await db.set_trace_callback(print)

            await db.execute(
                """
                INSERT INTO emotions(user_id, message, sentiment, lang, timestamp)
                VALUES (?, ?, ?, ?, ?)
                """, (user_id, message, sentiment, lang, datetime.now().isoformat())
            )
            await db.commit()
        return True
    except Exception as e:
        print(f'Ошибка сохранения: {e}')
        return False

async def get_last_record(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT * FROM emotions WHERE user_id=? ORDER BY ID DESC LIMIT 1",(user_id,) )
        return await cursor.fetchone()

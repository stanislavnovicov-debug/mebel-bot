import asyncio
import logging
from maxapi import Bot, Dispatcher
from maxapi.types import BotStarted, Command, MessageCreated
import sqlite3

logging.basicConfig(level=logging.INFO)

# Ваш токен из config
import config
bot = Bot(config.MAX_TOKEN)
dp = Dispatcher()

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('clients.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS clients
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  address TEXT,
                  stage TEXT,
                  deadline TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

# Добавление клиента
def add_client(name, address):
    conn = sqlite3.connect('clients.db')
    c = conn.cursor()
    c.execute("INSERT INTO clients (name, address, stage) VALUES (?, ?, ?)",
              (name, address, '🆕 Новый'))
    conn.commit()
    client_id = c.lastrowid
    conn.close()
    return client_id

# Получить список клиентов
def get_clients():
    conn = sqlite3.connect('clients.db')
    c = conn.cursor()
    c.execute("SELECT id, name, address, stage FROM clients ORDER BY created_at DESC")
    clients = c.fetchall()
    conn.close()
    return clients

# Ответ при запуске бота
@dp.bot_started()
async def bot_started(event: BotStarted):
    await event.bot.send_message(
        chat_id=event.chat_id,
        text='👋 Привет! Я ваш мебельный бот.\n\nНапишите /меню для списка команд.'
    )

# Команда /start
@dp.message_created(Command('start'))
async def cmd_start(event: MessageCreated):
    await event.message.answer(
        '🤖 Мебельный бот запущен!\n\n'
        'Доступные команды:\n'
        '/меню - Показать меню\n'
        '/new - Новый клиент\n'
        '/clients - Список клиентов'
    )

# Команда /меню
@dp.message_created(Command('меню'))
async def cmd_menu(event: MessageCreated):
    await event.message.answer(
        '📋 *Меню:*\n\n'
        '/new - Создать нового клиента\n'
        '/clients - Список всех клиентов\n'
        '/help - Помощь'
    )

# Команда /new
@dp.message_created(Command('new'))
async def cmd_new(event: MessageCreated):
    await event.message.answer(
        '📝 *Новый клиент*\n\n'
        'Введите имя клиента и адрес в формате:\n'
        '`Имя Адрес`\n\n'
        'Например: `Роман Ленина 5`'
    )

# Команда /clients
@dp.message_created(Command('clients'))
async def cmd_clients(event: MessageCreated):
    clients = get_clients()
    
    if not clients:
        await event.message.answer('📂 Список клиентов пуст.\n\nДобавьте первого через /new')
        return
    
    # Группируем по этапам
    stages = {'🆕 Новый': [], '📏 Замер': [], '🤝 Согласование': [], '💰 Продан': [], '✅ Готов': []}
    
    for client in clients:
        stage = client[3]
        if stage in stages:
            stages[stage].append(client)
    
    text = '📊 *Список клиентов:*\n\n'
    
    for stage, stage_clients in stages.items():
        if stage_clients:
            text += f'*{stage}*\n'
            for client in stage_clients:
                text += f'• {client[1]} ({client[2]})\n'
            text += '\n'
    
    await event.message.answer(text)

# Обработка обычного сообщения (создание клиента)
@dp.message_created()
async def handle_message(event: MessageCreated):
    text = event.message.body.text
    
    # Проверяем, не команда ли это
    if text.startswith('/'):
        return
    
    # Пытаемся создать клиента
    parts = text.split(' ', 1)
    if len(parts) == 2:
        name = parts[0]
        address = parts[1]
        
        client_id = add_client(name, address)
        
        await event.message.answer(
            f'✅ Клиент создан!\n\n'
            f'ID: {client_id}\n'
            f'Имя: {name}\n'
            f'Адрес: {address}\n'
            f'Этап: 🆕 Новый\n\n'
            f'Теперь напишите /clients чтобы увидеть список.'
        )
    else:
        await event.message.answer(
            '❓ Не понял команду.\n\n'
            'Напишите /меню для списка доступных команд.'
        )

async def main():
    init_db()
    print("🤖 Мебельный бот запускается...")
    print(f"Токен: {config.MAX_TOKEN[:20]}...")
    print("✅ Бот готов к работе!")
    
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

import time
import requests
import config

print("🤖 Запуск мебельного бота...")
print(f"Токен: {config.MAX_TOKEN[:20]}...")

# Тестовый запрос
try:
    response = requests.get('https://api.max.ru')
    print(f"API Max доступен: {response.status_code}")
except Exception as e:
    print(f"API Max недоступен: {e}")

print("✅ Бот готов к работе!")

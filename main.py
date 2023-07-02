import json
import os
from datetime import datetime
import requests
import telebot
import time

TOKEN = os.getenv('TOKEN_BOT')

bot = telebot.TeleBot('6238429367:AAEa1IYR19QPEqtQpHcpssTDhEytXE97O5I')

CURRENCY_RATES_FILE = "currency_rates.json"
API_KEY = os.getenv('EXCHANGE_RATE_API_KEY')


def get_currency_rate(currency: str) -> float:
    """Получает курс валюты от API и возвращает его в виде float"""

    url = f"https://api.apilayer.com/exchangerates_data/latest?base={currency}"
    response = requests.get(url, headers={'apikey': API_KEY})
    response_data = json.loads(response.text)
    rate = response_data["rates"]["RUB"]
    return rate


def save_to_json(data: dict) -> None:
    """Сохраняет данные в JSON-файл"""
    with open(CURRENCY_RATES_FILE, "a") as f:
        if os.stat(CURRENCY_RATES_FILE).st_size == 0:
            json.dump([data], f)
        else:
            with open(CURRENCY_RATES_FILE) as json_file:
                data_list = json.load(json_file)
            data_list.append(data)
            with open(CURRENCY_RATES_FILE, "w") as json_file:
                json.dump(data_list, json_file)


@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == '/start' or message.text == '/continue':
        bot.send_message(message.from_user.id, "Этот бот используется для получения курса валюты (USD или EUR)")
        bot.send_message(message.from_user.id, "Введите название валюты (/USD или /EUR)")
        bot.register_next_step_handler(message, my_main) #следующий шаг
    else:
        bot.send_message(message.from_user.id, 'Напишите /start')


def my_main(message):
    """
    Основная функция программы.
    Получает от пользователя название валюты — USD или EUR,
    получает и выводит на экран текущий курс валюты от API.
    Записывает данные в JSON-файл.
    """
    currency = message.text.upper()
    currency = currency.strip("/")
    if currency in ['USD', 'EUR']:
        rate = get_currency_rate(currency)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        bot.send_message(message.from_user.id, f"Курс {currency} к рублю: {rate:.2f}")
        data = {"currency": currency, "rate": rate, "timestamp": timestamp}
        save_to_json(data)
        bot.send_message(message.from_user.id, "Через минуту Вы можете повторить запрос")
        time.sleep(60)
        bot.send_message(message.from_user.id, "Чтобы продолжить напишите /continue")
        bot.register_next_step_handler(message, get_continue)
    else:
        bot.send_message(message.from_user.id, "Некорректный ввод")
        bot.send_message(message.from_user.id, "Чтобы продолжить напишите /continue")
        bot.register_next_step_handler(message, get_continue)



def get_continue(message):
    if message.text == '/start' or message.text == '/continue':
        bot.send_message(message.from_user.id, "Введите название валюты (/USD или /EUR)")
        bot.register_next_step_handler(message, my_main) #следующий шаг
    else:
        bot.send_message(message.from_user.id, 'Напишите /continue')
        bot.register_next_step_handler(message, start)



bot.polling(none_stop=True, interval=0)

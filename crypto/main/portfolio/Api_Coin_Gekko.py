import requests
from datetime import datetime
import csv
import psycopg2

#                                       """Coin Geeko API"""
# {'id': 'bitcoin', 'symbol': 'btc', 'name': 'Bitcoin'}
COINS = ['bitcoin', 'the-open-network']


def ping():
    url = "https://api.coingecko.com/api/v3/ping"

    headers = {
        "accept": "application/json",
        "x-cg-api-key": "CG-Yht7zs2aigen8xwtZY9c1xgP",
    }

    response = requests.get(url, headers)
    data = response.json()
    return data


def coins_list():
    url = "https://api.coingecko.com/api/v3/coins/list"

    headers = {
        "accept": "application/json",
        "x-cg-api-key": "CG-Yht7zs2aigen8xwtZY9c1xgP",
    }

    response = requests.get(url, headers)

    return response.json()


def supported_currencies_list():
    url = "https://api.coingecko.com/api/v3/simple/supported_vs_currencies"

    headers = {"accept": "application/json"}

    response = requests.get(url, headers=headers)

    return response.json()


def coin_price(currency_id):
    url_price = f"https://api.coingecko.com/api/v3/simple/price?ids={currency_id}&vs_currencies=usd&precision=4"

    headers = {
        "accept": "application/json",
        "x-cg-api-key": "CG-Yht7zs2aigen8xwtZY9c1xgP",
    }

    try:
        response = requests.get(url_price, headers=headers)
        response.raise_for_status()  # Проверяем HTTP-ошибки
        data = response.json()
        return data  # Возвращаем полный словарь, например: {'bitcoin': {'usd': 97485.3502}}
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса к API: {e}")
        return {}  # Возвращаем пустой словарь вместо None


def coin_historical_chart_data(coin_id, vs_currency, date_from, date_to):
    url = (f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart/range?vs_currency={vs_currency}"
           f"&from={date_from}&to={date_to}&precision=3")  # interval=daily&

    headers = {
        "accept": "application/json",
        "x-cg-api-key": "CG-Yht7zs2aigen8xwtZY9c1xgP"
    }

    response = requests.get(url, headers=headers)

    return response.json()


def save_data_csv():
    data = coin_historical_chart_data('the-open-network', 'usd', 1724225702, 1729496102)

    if 'error' not in data:

        csv_file = 'currency_data.csv'

        with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            writer.writerow(['datetaime', 'price', 'market_caps', 'total_volumes'])

            for i in range(len(data['prices'])):
                date = datetime.utcfromtimestamp(data['prices'][i][0] / 1000.0)
                formatted_date = date.strftime('%Y-%m-%d %H:%M:%S')
                price = data['prices'][i][1]
                market_cap = data['market_caps'][i][1]
                total_volume = data['total_volumes'][i][1]
                writer.writerow([formatted_date, price, market_cap, total_volume])

        print(f"Данные были сохранены в {csv_file}")
    else:
        print('Номер ошибки -', data['error']['status']['error_code'], 'Запись об ошибке -',
              data['error']['status']['error_message'])


def portfolio():
    currency_id = input("Введите id валют, которую хотите добавить \n").split()
    currency_list = []
    for i in currency_id:
        currency_list.append(coin_price(i))
    print(currency_list)


############################## PosgreSQL ###############################


conn_params = {
    'dbname': 'postgres_django',
    'user': 'postgres',
    'password': '1234',
    'host': 'localhost',
    'port': '5432'
}


def connect():
    try:
        conn = psycopg2.connect(**conn_params)
        print("Подключение успешно установлено")
        return conn
    except psycopg2.Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
        exit()


import csv
from datetime import datetime, timedelta


def save_multiple_months_data(start_timestamp, end_timestamp, coin_id='the-open-network', currency='usd',
                              csv_file='currency_data.csv'):
    """
    Сохраняет данные по криптовалюте за несколько месяцев в один файл.

    :param start_timestamp: Начальная временная метка (в формате UNIX).
    :param end_timestamp: Конечная временная метка (в формате UNIX).
    :param coin_id: ID криптовалюты на платформе API.
    :param currency: Валюта для отображения данных.
    :param csv_file: Имя CSV-файла для сохранения.
    """
    try:
        # Открываем файл для записи (добавление данных, если файл существует)
        with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            # Записываем заголовок файла, если он новый
            writer.writerow(['datetime', 'price', 'market_caps', 'total_volumes'])

            # Устанавливаем начальную точку
            current_start = start_timestamp
            while current_start < end_timestamp:
                # Устанавливаем конец текущего месяца
                current_end = min(current_start + 30 * 24 * 3600, end_timestamp)

                # Получаем данные за период
                data = coin_historical_chart_data(coin_id, currency, current_start, current_end)

                if 'error' not in data:
                    for i in range(len(data['prices'])):
                        date = datetime.utcfromtimestamp(data['prices'][i][0] / 1000.0)
                        formatted_date = date.strftime('%Y-%m-%d %H:%M:%S')
                        price = data['prices'][i][1]
                        market_cap = data['market_caps'][i][1]
                        total_volume = data['total_volumes'][i][1]
                        writer.writerow([formatted_date, price, market_cap, total_volume])

                    print(f"Данные за период {current_start} - {current_end} сохранены.")
                else:
                    print(f"Ошибка получения данных за период {current_start} - {current_end}: ",
                          data['error']['status']['error_message'])

                # Переходим к следующему месяцу
                current_start = current_end + 1
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")


# save_multiple_months_data(1669852761, 1701388761)

import csv
from datetime import datetime, timedelta


def save_bitcoin_prices():
    """
    Сохраняет данные по ценам на Bitcoin за период 2020–2024 в CSV файл.
    """
    start_date = datetime(2024, 8, 1)  # Начало периода
    end_date = datetime(2024, 12, 1)  # Конец периода (на 1 день меньше конца)
    coin_id = 'the-open-network'  # ID криптовалюты
    currency = 'usd'  # Валюта
    csv_file = 'ton_prices_2024_08-12.csv'  # Название файла

    # Преобразование дат в UNIX timestamp
    start_timestamp = int(start_date.timestamp())
    end_timestamp = int(end_date.timestamp())

    try:
        # Создаем файл для записи
        with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            # Записываем заголовок файла
            writer.writerow(['datetime', 'price', 'market_caps', 'total_volumes'])

            # Устанавливаем начальную точку
            current_start = start_timestamp
            while current_start < end_timestamp:
                # Устанавливаем конец текущего интервала (максимум 30 дней)
                current_end = min(current_start + 30 * 24 * 3600, end_timestamp)

                # Получаем данные за период
                data = coin_historical_chart_data(coin_id, currency, current_start, current_end)

                if 'error' not in data:
                    for i in range(len(data['prices'])):
                        date = datetime.utcfromtimestamp(data['prices'][i][0] / 1000.0)
                        formatted_date = date.strftime('%Y-%m-%d %H:%M:%S')
                        price = data['prices'][i][1]
                        market_cap = data['market_caps'][i][1]
                        total_volume = data['total_volumes'][i][1]
                        writer.writerow([formatted_date, price, market_cap, total_volume])

                    print(f"Данные за период {datetime.utcfromtimestamp(current_start).strftime('%Y-%m-%d')} "
                          f"- {datetime.utcfromtimestamp(current_end).strftime('%Y-%m-%d')} сохранены.")
                else:
                    print(
                        f"Ошибка получения данных за период {datetime.utcfromtimestamp(current_start).strftime('%Y-%m-%d')} "
                        f"- {datetime.utcfromtimestamp(current_end).strftime('%Y-%m-%d')}: ",
                        data['error']['status']['error_message'])

                # Переходим к следующему интервалу
                current_start = current_end + 1

    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")

# Запуск функции
# save_bitcoin_prices()

# print(coin_price('bitcoin'))

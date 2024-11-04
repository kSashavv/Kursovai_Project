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

    response = requests.get(url_price, headers=headers)

    return response.json()


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


# id_list = range(15058, 15071 + 1)
# print(id_list)
# conn = connect()
# try:
#     with conn.cursor() as cursor:
#         for i in range(15072, 15058, -1):
#             cursor.execute(f"""
#                 DELETE FROM portfolio_coinlist
#                 WHERE id = {i};
#             """)
#         conn.commit()
#         print("Данные успешно удалены из таблицы")
# except psycopg2.Error as e:
#     print(f"Ошибка при удалении данных: {e}")
#     conn.rollback()
#
# conn.close()

# DELETE
# FROM < имя_таблицы >
# WHERE
# id = < значение_id >;
# print(i)
# print(data)
# for i in data:
#     print(i['id'], i['symbol'], i['name'])


# def insert_data(conn, data):
#     try:
#         with conn.cursor() as cursor:
#             for item in data:
#                 cursor.execute("""
#                     INSERT INTO portfolio_coinlist (currency_id, symbol, name)
#                     VALUES (%s, %s, %s);
#                 """, (item['id'], item['symbol'], item['name']))
#         conn.commit()
#         print("Данные успешно вставлены в таблицу")
#     except psycopg2.Error as e:
#         print(f"Ошибка при вставке данных: {e}")
#         conn.rollback()
#
#
# conn = connect()
# insert_data(conn, data)
# conn.close()

# coins = coins_list()
# for i in coins:
#     if i['id'] == 'the-open-network':
#         print(i)
# print(coins)
# conn = connect()
# cursor = conn.cursor()
# cursor.execute("""
#                      INSERT INTO portfolio_coinlist (currency_id, symbol, name)
#                      VALUES (%s, %s, %s);
#                  """, ('the-open-network', 'ton', 'Toncoin'))
# conn.commit()
# conn.close()
# price = coin_price('the-open-network')
# print(price)
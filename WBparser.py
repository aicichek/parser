import requests
import pandas as pd
from bs4 import BeautifulSoup
from proxie import login, password
import time


def get_basket(short_id):
    if 0 <= short_id <= 143:
        return '01'
    elif 144 <= short_id <= 287:
        return '02'
    elif 288 <= short_id <= 431:
        return '03'
    elif 432 <= short_id <= 719:
        return '04'
    elif 720 <= short_id <= 1007:
        return '05'
    elif 1008 <= short_id <= 1061:
        return '06'
    elif 1062 <= short_id <= 1115:
        return '07'
    elif 1116 <= short_id <= 1169:
        return '08'
    elif 1170 <= short_id <= 1313:
        return '09'
    elif 1314 <= short_id <= 1601:
        return '10'
    elif 1602 <= short_id <= 1655:
        return '11'
    elif 1656 <= short_id <= 1919:
        return '12'
    else:
        return '13'

proxies = {
    # 'https': 'http://proxy_ip:proxy_port'
    'https': f'http://{login}:{password}@46.3.197.199:9734'
}

# Чтение CSV файла
df = pd.read_csv('input.csv')
result_df = pd.DataFrame(columns=['articul', 'imt_name', 'description', 'photo_url'])

# Пройдемся по каждой строке и выполним запрос
for index, row in df.iterrows():
    articul = row['articul']
    short_id = int(articul) // 100000  # Получение _short_id
    part = f'part{(articul) // 1000}'     # Получение part
    vol = f'vol{short_id}'       # Получение vol
    basket = get_basket(short_id)    # Получение номера basket
    url = f'https://basket-{basket}.wb.ru/{vol}/{part}/{articul}/info/ru/card.json'
    # print(url)
    # Выполнение запроса
    response = requests.get(url = url, proxies=proxies)
    
    if response.status_code == 200:
        data = response.json()
        # print(data)
        # Извлечение необходимых данных
        imt_name = data.get('imt_name', 'Нет данных')
        description = data.get('description', 'Нет данных')
        
        # Создание ссылки на фото товара
        photo_url = f'https://basket-{basket}.wb.ru/{vol}/{part}/{articul}/images/big/1.jpg'
        
        # Добавление данных в result_df
        result_df = result_df._append({'articul': articul, 'imt_name': imt_name, 'description': description, 'photo_url': photo_url}, ignore_index=True)
    else:
        print(f'Ошибка при выполнении запроса для артикула {articul}. Статус код: {response.status_code}')
    
    delay_seconds = 3
    time.sleep(delay_seconds)

# Запись результатов в output.csv
result_df.to_csv('output.csv', index=False)
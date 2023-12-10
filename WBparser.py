import requests
import pandas as pd
from proxie import *
import time
from itertools import cycle


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


proxies_list = [
    {'https': f'http://{login1}:{password1}@{purl1}'},
    {'https': f'http://{login2}:{password2}@{purl2}'},
    {'https': f'http://{login3}:{password3}@{purl3}'},
    # {'https': f'http://{login4}:{password4}@{purl4}'}
]
proxies_cycle = cycle(proxies_list)

# Чтение CSV файла
df = pd.read_csv('result_wb_resp.csv')
result_df = pd.DataFrame(columns=['TovCode','Nomenklatura','MarketPlace','articul MP', 'Название','Количество отзывов','Рейтинг', 'Ссылка на фото', 'Описание'])

# Пройдемся по каждой строке и выполним запрос
for index, row in df.iterrows():
    print(index)
    articul = row['M_Articul']
    TovCode = row['TovCode']
    Nomenklatura = row['Naimenov']
    short_id = int(articul) // 100000  # Получение _short_id
    part = f'part{(articul) // 1000}'     # Получение part
    vol = f'vol{short_id}'       # Получение vol
    basket = get_basket(short_id)    # Получение номера basket
    
    
    current_proxy = next(proxies_cycle)

    # Выполнение запроса
    try:
        url = f'https://basket-{basket}.wb.ru/{vol}/{part}/{articul}/info/ru/card.json'
        response = requests.get(url = url, proxies=current_proxy)
        url2 = f'https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=-1257786&spp=27&nm={articul}'
        response2 = requests.get(url = url2, proxies=current_proxy)
    except Exception as e:
        print(e)

    if response.status_code == 200 & response2.status_code == 200:
        data = response.json()
        # Извлечение необходимых данных
        imt_name = data.get('imt_name', 'Нет данных')
        description = data.get('description', 'Нет данных').strip().replace('\n', ' ').replace('  ',' ')

        data = response2.json()
        try:
            product_data = data.get('data', {}).get('products', [])[0]
            rating = product_data.get('reviewRating', 'Нет данных')
            reviews_count = product_data.get('feedbacks', 'Нет данных')
        except:
            rating = 0
            reviews_count = 0
        # Создание ссылки на фото товара
        photo_url = f'https://basket-{basket}.wb.ru/{vol}/{part}/{articul}/images/big/1.jpg'
        
        # Добавление данных в result_df
        result_df = result_df._append({'TovCode': TovCode,'Nomenklatura': Nomenklatura,'MarketPlace': 'wildberries','articul MP': articul, 'Название': imt_name, 'Описание': description, 'Ссылка на фото': photo_url, 'Рейтинг': rating,'Количество отзывов': reviews_count,}, ignore_index=True)
    else:
        print(f'Ошибка при выполнении запроса для артикула {articul}. Статус код: {response.status_code}')
    
    delay_seconds = 2
    time.sleep(delay_seconds)

# Запись результатов в output.csv
result_df.to_csv('output.csv', index=False, encoding='utf-8')

import pandas as pd
from bs4 import BeautifulSoup
import time
from selenium import webdriver
import seleniumbase as sb 
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
from proxie import *
from itertools import cycle
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By



proxies_list = [
    {'http': f'http://{login1}:{password1}@{purl1}'},
    {'http': f'http://{login2}:{password2}@{purl2}'},
    {'http': f'http://{login3}:{password3}@{purl3}'},
    {'http': f'http://{login4}:{password4}@{purl4}'}
]

def init_driver():
    driver = sb.Driver(browser='chrome', headless=False, uc=True, multi_proxy=proxies_list)

    wait = webdriver.Chrome.implicitly_wait(driver, 500.00)

    # Инициализация selenium-stealth
    stealth(driver,
            languages=["ry-RU", "ru"],
            vendor="Google Inc.",
            platform="Win64",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            wait=wait
            )

    return driver

def parse_product_page(driver, url):
    try:
        articul = url.rsplit('-', 1)[-1].split('&')[0]
        # driver.get(url)
        search_input = driver.find_element(By.CLASS_NAME, 'search-field-input')

        for _ in range(15):
            search_input.send_keys(Keys.BACK_SPACE)
            time.sleep(0.05)


        for char in articul:
            search_input.send_keys(char)
            time.sleep(0.2)  # Задержка в 0.2 секунды между символами (может потребоваться регулировка)
        search_input.send_keys(Keys.RETURN)


        time.sleep(2)  # Подождем некоторое время для полной загрузки страницы
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5) 

        # Получим HTML-код страницы
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')

        # Извлекаем описание
        description_tag = soup.find('div', class_='product-description').find('div', class_='text-block')
        description = description_tag.get_text(strip=True) if  description_tag else " "
        # description = " "

        title = soup.find('h1', class_='pdp-header__title').get_text(strip=True)

        rating_tag = soup.find('span', class_='reviews-rating__reviews-rating-count')
        rating = float(rating_tag.get_text(strip=True)) if rating_tag else 0.0

        reviews_count_tag = soup.find('span', class_='reviews-rating__reviews-count')
        try:
            reviews_count = int(reviews_count_tag.get_text(strip=True).split()[0])
        except: 
            reviews_count = 0
        
        photo_url_tag = soup.find('img', class_='inner-image-zoom_image')
        photo_url = photo_url_tag['src'] if photo_url_tag else None

        product_data = {
            'Название': title,
            'Количество отзывов': reviews_count,
            'Рейтинг': rating,
            'Ссылка на фото': photo_url,
            'Описание': description
        }

        return product_data

    except Exception as e:
        print(f"Ошибка при обработке товара: {url}")
        print(e)
        return None

def main():
    input_csv_path = 'productsmegam.csv'
    output_csv_path = 'mm result.csv'

    # Инициализируем веб-драйвер
    driver = init_driver()
    driver.get("""https://megamarket.ru/""")
    # Загрузим список товаров из CSV файла в DataFrame
    products_df = pd.read_csv(input_csv_path, delimiter=';')

    result_df = pd.DataFrame()
    # Добавим новые колонки в начало DataFrame
    result_df.insert(0, 'TovCode', products_df['Code'])
    result_df.insert(1, 'Nomenklatura', '')
    result_df.insert(2, 'MarketPlace', 'MegaMarket')
    result_df.insert(3, 'articul MP', products_df['Link'].apply(lambda x: x.rsplit('-', 1)[-1].split('&')[0]))
    
    # Продем по каждой строке в исходном DataFrame
    for index, row in products_df.iterrows():
        # driver = init_driver()

        product_url = row['Link']
        product_data = parse_product_page(driver, product_url)

        # Если товар не найден, пропустим его
        if product_data is None:
            continue

        # Обновим значения в DataFrame
        result_df.at[index, 'Название'] = product_data['Название']
        result_df.at[index, 'Количество отзывов'] = product_data['Количество отзывов']
        result_df.at[index, 'Рейтинг'] = product_data['Рейтинг']
        result_df.at[index, 'Ссылка на фото'] = product_data['Ссылка на фото']
        result_df.at[index, 'Описание'] = product_data['Описание']

    # Закроем веб-драйвер после завершения работы
    driver.quit()

    # Созраним результаты в CSV файл
    result_df.to_csv(output_csv_path, index=False)

if __name__ == "__main__":
    main()
import pandas as pd
from bs4 import BeautifulSoup
import time
from selenium import webdriver
import seleniumbase as sb 
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from proxie import login, password, url

def init_driver():
    # настройки прокси

    # proxy_url = f'http://{login}:{password}@46.3.197.199:9734'
    # proxy_url = f'http://46.3.197.199:9734'


    # Драйвер с использованием прокси, но на озоне не работает
    driver = sb.Driver(browser='chrome', headless=False, uc=True, )

    # driver = sb.Driver(browser='chrome', headless=False, uc=True)
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
        driver.get(url)
        html = driver.page_source
        if "CheckboxCaptcha-Button" in html:
            captcha_button = driver.find_element(By.CLASS_NAME, "CheckboxCaptcha-Button")
            captcha_button.click()


        time.sleep(2)  # Подождем некоторое время для полной загрузки страницы

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2) 

        # Получим HTML-код страницы
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')

        # Извлекаем описание
        description_div = soup.find('div', class_='_1n5cC')
        description_text = ''
        if description_div:
            description_text = ' '.join(span.get_text(strip=True) for span in description_div.find_all('span'))
        # Извлекаем остальные данные 
        title = soup.find('h1', attrs={'data-auto': 'productCardTitle'}).text.strip()
        # print(title)

        rating_span = soup.find('span', class_='ybvaC')
        reviews_span = soup.find('span', class_='_3i6i6')
        rating = float(rating_span.text) if rating_span else 0.0
        reviews_count = int(reviews_span.text.strip('()')) if reviews_span else 0


        img_div = soup.find('div', class_='cXkP_ gCOkS')
        img_src = img_div.find('img')['src'] if img_div else None

        product_data = {
            'Название': title,
            'Количество отзывов': reviews_count,
            'Рейтинг': rating,
            'Ссылка на фото': img_src,
            'Описание': description_text
        }

        return product_data

    except Exception as e:
        print(f"Ошибка при обработке товара: {url}")
        print(e)
        return None

def main():
    input_csv_path = 'products_yandex.csv'
    output_csv_path = 'result_yandex.csv'

    # Инициализируем веб-драйвер
    driver = init_driver()

    # Загрузим список товаров из CSV файла в DataFrame
    products_df = pd.read_csv(input_csv_path, delimiter=';')

    result_df = pd.DataFrame()
    # Добавим новые колонки в начало DataFrame
    result_df.insert(0, 'TovCode', products_df['Code'])
    result_df.insert(1, 'Nomenklatura', '')
    result_df.insert(2, 'MarketPlace', 'Yandex')
    result_df.insert(3, 'articul MP', products_df['Link'].apply(lambda x: x.rsplit('=', 1)[-1] if isinstance(x, str) else None))
    
    # Продем по каждой строке в исходном DataFrame
    for index, row in products_df.iterrows():
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
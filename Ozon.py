import pandas as pd
from bs4 import BeautifulSoup
import time
from selenium import webdriver
import seleniumbase as sb 
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth

# from proxie import login, password, url

def init_driver():
    # настройки прокси

    # proxy_url = f'http://{login}:{password}@46.3.197.199:9734'
    # proxy_url = f'http://46.3.197.199:9734'


    # Драйвер с использованием прокси, но на озоне не работает
    # driver = sb.Driver(browser='chrome', headless=False, uc=True, proxy=proxy_url)

    driver = sb.Driver(browser='chrome', headless=False, uc=True)
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
        driver.get(url + '/?oos_search=false')
        time.sleep(2)  # Подождем некоторое время для полной загрузки страницы

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5) 

        # Получим HTML-код страницы
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')

        # Извлекаем описание
        description_div = soup.find('div', {'id': 'section-description'})
        description_text = ''
        if description_div:
            description_text = ' '.join(span.get_text(strip=True) for span in description_div.find_all('span'))

        title = soup.select_one('div[data-widget="webProductHeading"] h1').text.strip()
        web_review_elements = soup.find_all(attrs={"data-widget": "webReviewProductScore"})
        res = str(web_review_elements)
        end_index = res.find("отзыв")
        result_text = res[0:end_index].strip()
        if "стави" in result_text:
            reviews_count = 0
        else:
            start_index = result_text.rfind(">")
            reviews_count = result_text[start_index+1:].strip()

        end_index = res.find("""%""")
        result_text = res[0:end_index].strip()
        start_index = result_text.rfind(""":""")
        rating = result_text[start_index+1:].strip()
        rating = float(rating)
        rating=rating/20


        web_gallery_elements = soup.find_all(attrs={"data-widget": "webGallery"})
        img_src = " "
        for web_gallery_element in web_gallery_elements:
            img_elements = web_gallery_element.find_all('img')

            if img_elements:
                img_src = img_elements[0]['src']

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
    input_csv_path = 'products.csv'
    output_csv_path = 'ozon result.csv'

    # Инициализируем веб-драйвер
    driver = init_driver()

    # Загрузим список товаров из CSV файла в DataFrame
    products_df = pd.read_csv(input_csv_path, delimiter=';')

    result_df = pd.DataFrame()
    # Добавим новые колонки в начало DataFrame
    result_df.insert(0, 'TovCode', products_df['Code'])
    result_df.insert(1, 'Nomenklatura', '')
    result_df.insert(2, 'MarketPlace', 'Ozon')
    result_df.insert(3, 'articul MP', products_df['Link'].apply(lambda x: x.rsplit('/', 1)[-1] if isinstance(x, str) else None))
    
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

# Пасереры OZON, Яндекс маркет, wildberries

# Ozon
Берет ссылки на товары из файла products.csv
Считывает с каждого навание, описание, рейтинг, количество отзывов, ссылку на фото.
Все записывает в датафрейм, в коце все записывает в файл.
Работает максимально стабильно.

# Яндекс маркет
Берет ссылки на товары из файла products_yandex.csv
Считывает с каждого навание, описание, рейтинг, количество отзывов, ссылку на фото.
Все записывает в датафрейм, в коце все записывает в файл.
Яндекс переодически требует ввода капчи, пока он требует простого клика по ней - все стабильно
как только он требует решить что-то - все ломается.
При запуске с неподозрительных ip может очень долго не требовать решения
2500 товаров за раз обрабатывает стабильно

# wildberries
Берет ссылки на товары из файла products_yandex.csv
Считывает с каждого навание, описание, рейтинг, количество отзывов, ссылку на фото.
Все записывает в датафрейм, в коце все записывает в файл.
Так как ВБ это позволяет и в угоду скорости - реализовано реквестами, а не через селениум
Однако за такое ВБ блокирует ip переодически, для этого реализовано использование множественного прокси
настраивается в proxie.py
Рекомендуется хотя-бы 3 разных прокси использовать
При использовании большего числа, можно уменьшать задержу тем самым увеличивая скорость.

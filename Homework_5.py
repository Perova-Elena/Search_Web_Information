# Загружаем необходимые библиотеки
from pymongo import MongoClient
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options

# Создаем клиента для связи с базой данных MongoDB
client = MongoClient('127.0.0.1', 27017)
mongo_base = client['mvideo'] # Создаем базу данных по магазину МВидео
collection = mongo_base['in_trend'] # Создаем коллекцию в новой базе, куда пойдет информация по товарам "В Тренде".

# Создаем обьект-драйвер класса Chrome, с которым мы и будем работать:
driver = webdriver.Chrome(executable_path='./chromedriver')
driver.implicitly_wait(10)      # Вставим задержку по времени, чтобы старница успевала полностью загружаться

# Делаем get-запрос к главной странице МВидео:
driver.get('https://www.mvideo.ru/')
# assert 'М.Видео' in driver.title # Проверка действительно ли открылся сайт МВидео

# Начинаем обработку страницы:

lebel = driver.find_element(By.XPATH, "//a[@class='logo ng-tns-c279-2 ng-star-inserted']")
while True:
    try:
        elem = driver.find_element(By.XPATH, "//button[@class='tab-button ng-star-inserted']//span[@class='title']")
        break
    except exceptions.NoSuchElementException:
        lebel.send_keys(Keys.PAGE_DOWN)
elem.click() # Кликаем на кнопку "В тренде" (Пробовала, работает!)

# Выбираем карусель из 16 элементов-товаров в категории "В тренде"
products = driver.find_elements(By.XPATH,
                                '//mvid-carousel[@class="carusel ng-star-inserted"]//mvid-product-cards-group//div[contains(@class, "product-mini-card__image")]//a')
links = []
# Составляем список из ссылок на товары категории "В тренде":
for i in products:
    link = i.get_attribute('href')
    links.append(link)

# Далее заходя в каждую ссылку драйвером пополняем базу словарями с данными о каждом продукте, в который вошли:
for link in links:
    product = {}
    product['link'] = link
    driver.implicitly_wait(10)
    driver.get(link)   # Заход в ссылку
    product['name'] = driver.find_element(By.XPATH, '//h1').get_attribute('innerHTML')
    product['price'] = driver.find_element(By.XPATH,
                                           '//mvideoru-product-details-card//span[@class="price__main-value"]').get_attribute(
        'innerHTML').replace('&nbsp', '').replace(';', '').replace('₽', '')
    try:
        product['image'] = driver.find_element(By.XPATH,
                                               '//div[contains(@class, "zoomable-image")]').value_of_css_property(
            "background-image").replace('url(', '').replace(')', '').replace('"', '')
    except exceptions.NoSuchElementException:
        product['image'] = driver.find_element(By.XPATH, '//img[contains(@class, "zoomable-image")]').get_attribute(
            'src')
    collection.update_one({'link': product['link']}, {'$set': product}, upsert=True)

driver.quit()
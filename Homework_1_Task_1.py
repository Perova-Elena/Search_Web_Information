import requests    # Импортируем модуль для запросов requests
import json
from pprint import pprint # Для более наглядного представления словаря json импортирем функцию pprint

user = 'Perova-Elena'  # Вынесем имя пользователя в отдельную переменную для удобства
url = f'https://api.github.com/users/{user}/repos'  # Находим нужное нам API на портале github

responсe = requests.get(url).json()       # Получаем ответ от сервера в виде списка и сразу представляем его в формате json
pprint(responсe)                            # Посмотрим на результат вывода, видим, что нам отсюда нужно
                                            # не все. Названия репозиториев хранятся под ключем "name".
final_list = [{user: i['name']} for i in responсe]   # Создадим список словарей из репозиториев нужного пользователя
pprint (final_list)

with open('responce.json', 'w', encoding='utf-8') as file:     # Записываем список репозиториев в файл .json
     json.dump(final_list, file, indent=4)
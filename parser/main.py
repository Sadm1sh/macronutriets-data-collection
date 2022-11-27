import random
import time
import requests
from bs4 import BeautifulSoup
import json
import csv
url = "https://health-diet.ru/table_calorie/?utm_source=leftMenu&utm_medium=table_calorie"
headers = {
    'accept': '',  # задаём загаловки что-бы сайт не считал нас за бота
    'user-agent': ''
}
req = requests.get(url, headers=headers)
src = req.text

with open('index.html', 'w', encoding='utf-8') as file:
    file.write(src)

with open('index.html', 'r', encoding='utf-8') as file:
    src = file.read()

soup = BeautifulSoup(src, 'lxml')
all_categories_hrefs = soup.find_all(class_='mzr-tc-group-item-href')
all_categories_dict = {}

for item in all_categories_hrefs:
    item_text = item.text
    item_href = 'https://health-diet.ru' + item.get('href')
    all_categories_dict[item_text] = item_href

with open('categories.json', 'w', encoding='utf-8') as file:
    json.dump(all_categories_dict, file, indent=4, ensure_ascii=False)

with open('categories.json', encoding='utf-8') as file:
    categories = json.load(file)
iteration_count = int(len(categories)) - 1
print(f'Всего иттераций: {iteration_count}')
count = 0
for category_name, category_href in categories.items():
    try:
        iteration_count = iteration_count - 1
        rep = [', ', ' ', "'", "-"]
        for item in rep:
            if item in category_name:
                category_name = category_name.replace(item, "_")
        req = requests.get(category_href, headers=headers)
        src = req.text

        with open(f'parser/date/{count}_{category_name}.html', 'w', encoding='utf-8') as file:
            file.write(src)
        with open(f'parser/date/{count}_{category_name}.html', encoding='utf-8') as file:
            src = file.read()
        soup = BeautifulSoup(src, "lxml")

        # Прооверка на наличие таблицы
        alert_block = soup.select_one('.uk-alert-danger')
        if alert_block is not None:
            continue

        # Собираем заголовки столбцов таблицы
        column_header = soup.select(".uk-overflow-container tr th")
        product = column_header[0].text
        calories = column_header[1].text
        proteins = column_header[2].text
        fats = column_header[3].text
        carbohydrates = column_header[4].text

        with open(f"parser/date/{count}_{category_name}.csv", 'w') as file:
            writer = csv.writer(file, delimiter=';', lineterminator='\n')
            writer.writerow(
                (
                    product,
                    calories,
                    proteins,
                    fats,
                    carbohydrates
                )
            )
        column_header = soup.select(".uk-overflow-container tbody tr")
        product_info = []
        for item in column_header:
            product_tds = item.select("td")
            title = product_tds[0].text
            calories = product_tds[1].text
            proteins = product_tds[2].text
            fats = product_tds[3].text
            carbohydrates = product_tds[4].text

            product_info.append(
                [
                    {
                        "Title": title,
                        "Calories": calories,
                        "Proteins": proteins,
                        "Fats": fats,
                        "Carbohydrates": carbohydrates
                    }
                ]
            )

            with open(f"parser/date/{count}_{category_name}.csv", "a") as file:
                writer = csv.writer(file, delimiter=';', lineterminator='\n')
                writer.writerow(
                    (
                        title,
                        calories,
                        proteins,
                        fats,
                        carbohydrates
                    )
                )

            with open(f"parser/date/{count}_{category_name}.json", "w", encoding="utf-8") as file:
                json.dump(product_info, file, indent=4, ensure_ascii=False)
        count += 1
        print(f'Итерация номер {count}, {category_name} записан...')

        if iteration_count == 0:
            print('Работа завершена')
            break
    except UnicodeEncodeError:
        continue
    print(f'Осталось итераций: {iteration_count}')
    time.sleep(random.randrange(2, 4))

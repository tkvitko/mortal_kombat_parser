import _thread
import csv
from sys import argv
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

matches = []
interested_counts = ['0:5', '5:0', '1:2', '2:1', '1:3', '3:1']
refresh_timeout = 10
refresh_timeout_short = 3
score_of_end = 5


def parse_sport(url):

    chrome_options = Options()
    chrome_options.add_argument('start-maximized')
    # на всякий случай, без этого могло упасть по timeout:
    chrome_options.add_argument('enable-features=NetworkServiceInProcess')
    chrome_options.add_argument('--no-sandbox')
    driver = webdriver.Chrome('./chromedriver', options=chrome_options)

    global matches
    numbers = set()

    driver.get(url)

    while True:

        try:
            sport_name_block = driver.find_element_by_class_name('c-events__item_head')
            sport_name = sport_name_block.find_element_by_class_name('c-events__name').text
            # print(sport_name)
            words = sport_name.split(' ')
            if words[0] == 'Mortal':
                pass
            else:
                break
        except:
            continue

        try:
            matches_obj_list = driver.find_elements_by_class_name('c-events__item_col')
        except:
            continue

        for match_obj in matches_obj_list:
            try:
                match = {}
                element = WebDriverWait(driver, 30).until(
                    ec.presence_of_element_located((By.TAG_NAME, "a")))
                a = match_obj.find_element_by_tag_name('a')
                match_url = a.get_attribute('href')
                spans = a.find_elements_by_tag_name('span')
                match_number = spans[-1].text  # вынимаем номер матча

                round = None  # по каждому матчу проверяем, начался ли он, или это только прогноз
                try:
                    subitem = match_obj.find_element_by_class_name('c-events-scoreboard__subitem')
                    round = subitem.find_element_by_class_name('c-events__overtime')
                except:
                    pass

                if round:  # если матч уже начался и есть текущий раунд

                    if match_number not in numbers:  # если это новый номер матча
                        match['number'] = match_number  # заполняем номер матча
                        match['url'] = match_url  # заполняем url на матч
                        # match['gone'] = False  # помечаем, что еще не анализировали
                        matches.append(match)  # добавляем матч в общий список

                        numbers.add(match_number)  # добавляем номер матча в список уникальных номеров
            except:
                continue

            sleep(refresh_timeout)


def parse_match(url):

    chrome_options = Options()
    chrome_options.add_argument('start-maximized')
    # на всякий случай, без этого могло упасть по timeout:
    chrome_options.add_argument('enable-features=NetworkServiceInProcess')
    chrome_options.add_argument('--no-sandbox')
    driver = webdriver.Chrome('./chromedriver', options=chrome_options)

    max_score = 0
    scores_pairs_list = []
    times_list = []
    koef_pairs_list = []
    is_interested = False

    driver.get(url)

    while max_score < score_of_end:

        # Сбор счета
        try:
            scores_pair = ''
            scores_obj = driver.find_elements_by_class_name('c-tablo-count__num')

            for score_obj in scores_obj:  # для каджого блока очков
                score = score_obj.text  # вынимаем значение очков
                scores_pair += score  # добавляем значение в строку счета
                scores_pair += ':'  # добавляем разделитель
                if int(score) > max_score:  # если текущее значение больше текущего максимума
                    max_score = int(score)  # максимум становится текущим значением

            scores_pair = scores_pair[:-1]  # отрезаем лишний разделительвконце строки
            if scores_pairs_list.count(scores_pair) == 0:  # добавляем счет в список счетов
                scores_pairs_list.append(scores_pair)

        except:
            pass

        # Сбор времени раундов
        try:
            element = WebDriverWait(driver, 60).until(
                ec.presence_of_element_located((By.CLASS_NAME, "cyber-stat-table__body")))
            table_obj = driver.find_element_by_class_name('cyber-stat-table__body')  # находим таблицу
            cols_obj = table_obj.find_elements_by_class_name('cyber-stat-table__col')  # находим колонки

            times_list = []
            for col_obj in cols_obj:  # для каждой колонки
                time = col_obj.find_elements_by_class_name('cyber-stat-table__cell')[
                    -1].text  # время - последняя строка
                times_list.append(time)  # добавляем время в список
        except:
            pass

        # Сбор продолжительности раундов из талицы под основной
        try:
            element = WebDriverWait(driver, 30).until(
                ec.presence_of_element_located((By.CLASS_NAME, "bet_group_col")))
            blocks = driver.find_elements_by_class_name('bet_group_col')
            right_block = blocks[1]
            upper_block = right_block.find_element_by_class_name('betCols2')
            divs = upper_block.find_elements_by_tag_name('div')
            # print(f'{url} koefs block founded')
            koef_pair = ''
            # for div in divs[2:4]:
            #     koef = div.find_element_by_class_name('koeff').get_attribute('data-coef')
            #     koef_pair += koef
            #     koef_pair += ','
            # if koef_pairs_list.count(koef_pair) == 0:
            #     koef_pairs_list.append(koef_pair)
            koef = divs[2].find_element_by_class_name('bet_type').text
            words = koef.split(' ')
            result = words[2]
            if koef_pairs_list.count(result) == 0:
                koef_pairs_list.append(result)
        except:
            pass

        if max_score >= score_of_end - 1:  # если счет уже поднялся до 4х
            sleep(refresh_timeout_short)  # обновляем страницу часто, чтобы не упустить финал
        else:  # иначе
            sleep(refresh_timeout)  # обновляем страницу редко

    driver.close()

    # Проверка, является ли матч "тем самым"
    for count in interested_counts:
        if count in scores_pairs_list:
            is_interested = True

    return is_interested, times_list, scores_pairs_list, koef_pairs_list


def get_first_from_list(matches_list):
    try:
        match = matches.pop(0)  # пробуем забрать первый элемент
        number = match['number']
        url = match['url']

        match_dict = {'number': number, 'is_interested': parse_match(url)[0], 'times': parse_match(url)[1],
                      'scores': parse_match(url)[2], 'koefs': parse_match(url)[3]}
        # остальные значения вынимаем со страницы матча

        # по завершении матча записываем всю информацию в итоговый csv
        with open(csv_file, 'a', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['number', 'is_interested', 'times', 'scores', 'koefs'],
                                    delimiter=';')
            writer.writerow(match_dict)
            print(f"{number} has been added to {csv_file} with result={match_dict['is_interested']}")

    except:
        pass


if __name__ == "__main__":

    script, url, csv_file = argv

    # Тестирование:
    # url, csv_file = "https://one-xskbdc.world/ru/live/Mortal-Kombat/1252965-Mortal-Kombat-X/", 'matches.csv'

    # асинхронно запускаем парсер матчей
    _thread.start_new_thread(parse_sport, (url,))

    # асинхронно работаем с каждым взятым матчем
    while True:
        if len(matches) > 0:
            _thread.start_new_thread(get_first_from_list, (matches,))

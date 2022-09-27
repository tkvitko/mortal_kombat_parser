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
                _ = WebDriverWait(driver, 30).until(
                    ec.presence_of_element_located((By.TAG_NAME, "a")))
                a = match_obj.find_element_by_tag_name('a')
                match_url = a.get_attribute('href')
                spans = a.find_elements_by_tag_name('span')
                match_number = spans[-1].text  # getting the number of match

                round_ = None  # checking for each match if it already starts or it is only forecast
                try:
                    sub_item = match_obj.find_element_by_class_name('c-events-scoreboard__subitem')
                    round_ = sub_item.find_element_by_class_name('c-events__overtime')
                except:
                    pass

                if round_:  # if match has been started already and there is an actual round

                    if match_number not in numbers:  # if it is new number of match
                        match['number'] = match_number  # fill match number
                        match['url'] = match_url  # fill match url
                        # match['gone'] = False  # fill match not yet analysed
                        matches.append(match)  # add match to the list

                        numbers.add(match_number)  # add match number to the list of uniq match numbers
            except:
                continue

            sleep(refresh_timeout)


def parse_match(url):
    chrome_options = Options()
    chrome_options.add_argument('start-maximized')
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

        # getting score
        try:
            scores_pair = ''
            scores_obj = driver.find_elements_by_class_name('c-tablo-count__num')

            for score_obj in scores_obj:  # for every block of scores
                score = score_obj.text  # getting scores value
                scores_pair += score  # add value to the score string
                scores_pair += ':'  # add delimiter
                if int(score) > max_score:  # if current value is bigger than current max
                    max_score = int(score)  # refresh current max

            scores_pair = scores_pair[:-1]  # remove redundant delimiter from the end of the string
            if scores_pairs_list.count(scores_pair) == 0:  # add score to the list of scores
                scores_pairs_list.append(scores_pair)

        except:
            pass

        # getting times of rounds
        try:
            _ = WebDriverWait(driver, 60).until(
                ec.presence_of_element_located((By.CLASS_NAME, "cyber-stat-table__body")))
            table_obj = driver.find_element_by_class_name('cyber-stat-table__body')  # find table
            cols_obj = table_obj.find_elements_by_class_name('cyber-stat-table__col')  # find columns

            times_list = []
            for col_obj in cols_obj:  # for each column
                time = col_obj.find_elements_by_class_name('cyber-stat-table__cell')[
                    -1].text  # time is in the last string
                times_list.append(time)  # adding time to the list
        except:
            pass

        # getting the round's durations from the botton row
        try:
            _ = WebDriverWait(driver, 30).until(
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

        if max_score >= score_of_end - 1:  # if the score is already above 4
            sleep(refresh_timeout_short)  # update the page more frequent not to miss the end of match
        else:
            sleep(refresh_timeout)  # update the page rarely

    driver.close()

    # check if this match is interested
    for count in interested_counts:
        if count in scores_pairs_list:
            is_interested = True

    return is_interested, times_list, scores_pairs_list, koef_pairs_list


def get_first_from_list(matches_list):
    try:
        match = matches.pop(0)  # try to get the first element
        number = match['number']
        url = match['url']

        match_dict = {'number': number, 'is_interested': parse_match(url)[0], 'times': parse_match(url)[1],
                      'scores': parse_match(url)[2], 'koefs': parse_match(url)[3]}
        # other values will be parsed from match's page

        # write the values to the result csv-file after match ends
        with open(csv_file, 'a', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['number', 'is_interested', 'times', 'scores', 'koefs'],
                                    delimiter=';')
            writer.writerow(match_dict)
            print(f"{number} has been added to {csv_file} with result={match_dict['is_interested']}")

    except:
        pass


if __name__ == "__main__":

    script, url, csv_file = argv

    # Testing:
    # url, csv_file = "https://one-xskbdc.world/ru/live/Mortal-Kombat/1252965-Mortal-Kombat-X/", 'matches.csv'

    # asynchronously starts the matches parser
    _thread.start_new_thread(parse_sport, (url,))

    # asynchronously work with each match
    while True:
        if len(matches) > 0:
            _thread.start_new_thread(get_first_from_list, (matches,))

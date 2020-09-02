Подготовка к работе
Для работы парсеру нужен chromedriver. Скачать с https://chromedriver.chromium.org/downloads и положить файл в папку рядом со скриптом.

Запуск
Скрипт запускается с двумя параметрами: url начальной страницы и имя файла, в который складывать результат (заранее создавать файл не нужно; если его нет, скрипт его создаст; если он есть, скрипт будет дописывть в него)
Пример запуска:
python3.7 main.py "https://one-xskbdc.world/ru/live/Mortal-Kombat/1252965-Mortal-Kombat-X/" matches.csv
python3.7 main.py "https://one-xskbdc.world/ru/live/Mortal-Kombat/2068436-Mortal-Kombat-11/" matches_2.csv


Остановка
Остановка прямо в консоли - ctrl+c. По итогу остановки может выпасть исключение, это нормально, всё в порядке.

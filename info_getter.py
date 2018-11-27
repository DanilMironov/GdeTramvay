from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.parse import quote
from urllib.error import HTTPError, URLError
import re


class InfoGetter:
    def __init__(self):
        self._homepage = 'http://online.ettu.ru'
        self._first_letters = '1,4,7,А,Б,В,Г,Д,Е,Ж,З,И,К,Л,М,Н,' \
                              'О,П,Р,С,Т,У,Ф,Х,Ц,Ч,Ш,Щ,Э,Ю,Я'

    @staticmethod
    def _get_user_data(input_text=''):
        return input(input_text + '\n')

    def _get_stations_dict(self):
        first_letter = self._get_user_data('Пожалуйста введите первую '
                                           'букву названия остановки').upper()
        if first_letter in self._first_letters:
            page = self._get_html(self._homepage +
                                  '/stations/' +
                                  quote(first_letter))
        else:
            raise Exception('Станции с таким именем не существует')
        answ = self._get_user_data('Трамвай или троллейбус?').lower()
        is_tram = answ == 'трамвай'
        needed_piece = self._get_needed_piece(page, is_tram)
        soup = BeautifulSoup(needed_piece, 'html.parser')
        raw_list = soup.find_all('a')
        return self._create_stations_dict(raw_list)

    @staticmethod
    def _create_info_table(page):
        soup = BeautifulSoup(page, 'html.parser')
        step1 = soup.find_all('div')[0].find_all('div')
        table = []
        for element in step1:
            line = element.find_all('div')
            if line:
                new_element = re.findall('>([ а-я\d]+)<', str(line))
                table.append(new_element)
        return table

    def get_info_table(self):
        station_page = self._get_station_page()
        info_table = self._create_info_table(station_page)
        table = 'Маршрут   Время ожидания   Расстояние\n'
        for line in info_table:
            app = '{0}\t\t{1}\t\t{2}'.format(line[0], line[1], line[2])
            table = table + app + '\n'
        return table

    def _get_station_page(self):
        stations = self._get_stations_dict()
        print('\nВыберите станцию\n')
        for station in stations.keys():
            print(station)
        answer = self._get_user_data()
        station_code = stations[answer]
        address = self._homepage + station_code
        return self._get_html(address)

    def _create_stations_dict(self, raw_list):
        result = {}
        stations = self._create_list_of_station(raw_list)
        numbers = self._create_list_of_numbers(raw_list)
        for i in range(len(stations)):
            result[stations[i]] = numbers[i]
        return result

    @staticmethod
    def _create_list_of_numbers(raw_list):
        list_of_numbers = []
        for element in raw_list:
            num = str(element.get('href'))
            if num.startswith('/station'):
                list_of_numbers.append(num)
        return list_of_numbers

    @staticmethod
    def _create_list_of_station(raw_list):
        list_of_stations = []
        for element in raw_list:
            station = (re.findall(r'<a href="/station/\d+">(.+)</a>',
                                  str(element)))
            if station:
                list_of_stations.append(station[0])
        return list_of_stations

    @staticmethod
    def _get_needed_piece(html: str, is_tram: bool):
        lindex = html.index('Трамваи')
        boundary = html.index('Троллейбусы')
        rindex = html.index('Замечания по сервису')
        if is_tram:
            needed_piece = html[lindex:boundary]
        else:
            needed_piece = html[boundary:rindex]
        return needed_piece

    @staticmethod
    def _get_html(address):
        try:
            with urlopen(address) as page:
                return page.read().decode('utf-8', errors='ignore')
        except(HTTPError, URLError):
            raise Exception('Что-то пошло не так')

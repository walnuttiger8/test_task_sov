from urllib.parse import urlencode, quote_plus
import requests
from bs4 import BeautifulSoup as Bs
from headers import headers
from list_fias_parser import ListFiasParser as Lfp
from abc import abstractmethod


class SessionExpiredException(Exception):
    pass


class Search:
    _base_url = "https://www.reformagkh.ru"

    def __init__(self, session: requests.Session):
        self.url = Search._base_url + "/search"
        self.session = session
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Cookie": headers["Cookie"],
        }

    def get_links(self, soup: Bs):
        table = soup.find("table")
        if not table:
            return []
        result = list()
        for row in table.find_all("tr"):
            a = row.find("a")
            if a:
                result.append(a["href"])
        return result

    @abstractmethod
    def search(self, region: str, settlement: str, street: str, house: str):
        pass


class SimpleSearch(Search):

    def __init__(self, session: requests.Session):
        super().__init__(session)
        self.url += "/houses"

    def search(self, region: str, settlement: str, street: str, house: str):
        query = self.get_query_string(region, settlement, street, house)
        params = {
            "query": query,
        }
        response = self.session.get(self.url, params=params, headers=self.headers)
        if response.status_code != 200:
            raise SessionExpiredException("Недействительная сессия")
        soup = Bs(response.content, "html.parser")
        return self.get_links(soup)

    @staticmethod
    def get_query_string(region: str, settlement: str, street: str, house: str):
        region = region.split()[0] if len(region.split()) > 1 else region
        settlement = settlement or region
        return " ".join([region, settlement, street, house])


class AdvancedSearch(Search):
    def __init__(self, session: requests.Session):
        super().__init__(session)
        self.url += "/houses-advanced"
        self.headers["Content-Type"] = "application/x-www-form-urlencoded"

    def search(self, region: str, settlement: str, street: str, house: str):
        params = {
            "region": region or "",
            "region-guid": "",
            "district": "",
            "district-guid": "",
            "settlement": settlement or "",
            "settlement-guid": "",
            "street": street or "",
            "street-guid": "",
            "house": house or "",
            "house-guid": "",
        }
        lfp = Lfp()
        params.update(lfp.get_guids(params))
        if not params["house-guid"]:
            return []
        response = self.session.post(self.url, data=urlencode(params, quote_via=quote_plus), headers=self.headers)
        with open('last_requested_page.html', "wb") as file:
            file.write(response.content)
        if response.text.startswith("<script") or response.status_code != 200:
            raise SessionExpiredException("Сессия недействительна")
        soup = Bs(response.content, "html.parser")
        return self.get_links(soup)


class AddressParser:
    """
    Основной класс для парсинга.

    Простой поиск: simple_search()
    Расширеннный поиск: advanced_search()

    Получение информации по результатам поиска: get_data()
    """
    _base_url = "https://www.reformagkh.ru"

    def __init__(self, search_class=AdvancedSearch):
        self.session = requests.Session()
        self.headers = headers
        self.search = search_class(self.session)

    def get_data(self, link: str) -> dict:
        """
        Получает необходимые данные из информации о доме
        :param link: обрезанная ссылка на описание дома
        :return: словарь с данными
        """
        url = AddressParser._base_url + link + "#content"
        url = url.replace("view", "passport")
        response = self.session.get(url, headers={"Accept": headers["Accept"]})
        with open('last_requested_page.html', "wb") as file:
            file.write(response.content)
        soup = Bs(response.content, "html.parser")
        house_table = soup.find("table", attrs={"id": "profile-house-style"})
        constructive_table = soup.find("table", attrs={"id": "house-passport-constructive"})
        house_profile = AddressParser._parse_table(house_table)
        constructive = AddressParser._parse_table(constructive_table)
        constructive = {"Тип перекрытий": constructive.get("Тип перекрытий"),
                        "Материал несущих стен": constructive.get("Материал несущих стен")}
        house_profile = {
            "Год ввода в эксплуатацию": house_profile.get("Год ввода дома в эксплуатацию:"),
            "Количество этажей": house_profile.get("Количество этажей, ед:"),
            "Последнее изменение анкеты": house_profile.get(
                "По данным Фонда ЖКХ информация последний раз актуализировалась:"),
            "Серия, тип постройки здания": house_profile.get("Серия, тип постройки здания:"),
            "Тип дома": house_profile.get("Тип дома:"),
            "Кадастровый номер": house_profile.get("кадастровый номер земельного участка"),
        }
        house_profile.update(constructive)
        return house_profile

    @staticmethod
    def _parse_table(table):
        if not table:
            return {}
        result = dict()
        for i in table.find_all("i"):
            i.decompose()
        for row in table.find_all("tr", recursive=False):
            cells = row.find_all("td", attrs={"style": ""}, recursive=False)
            if len(cells) < 2:
                continue
            key = " ".join(cells[0].text.split())
            value = " ".join(cells[-1].text.split())
            result[key] = value

        return result

import requests
from phpsessid import get_phpsessid


class ListFiasParser:
    """
    Класс для получения guid каждого элемента поиска при расширенном поиске
    """

    class Levels:
        REGION = "region",
        DISTRICT = "district",
        SETTLEMENT = "settlement",
        STREET = "street",
        HOUSE = "house",

    _base_url = "https://www.reformagkh.ru"

    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 YaBrowser/21.6.0.616 Yowser/2.5 Safari/537.36",
            "Cookie": "",
        }
        self.update_session()

    def update_session(self):
        sessid = get_phpsessid()
        self.headers["Cookie"] = f"PHPSESSID={sessid['PHPSESSID']}"

    @staticmethod
    def search(list_fias: dict, value: str):
        for key in list_fias:
            if key.lower().find(value.lower()) != -1:
                return key, list_fias[key]

        return "", ""

    def get_guid(self, level, parent, key):
        if not parent or not key:
            if level == ListFiasParser.Levels.REGION:
                pass
            else:
                return "", ""
        list_fias = self.get_list_fias(level, parent, key)
        return ListFiasParser.search(list_fias, key)

    def get_list_fias(self, level, parent, term="") -> dict:
        url = ListFiasParser._base_url + "/myhouse/list-fias"
        params = {
            "level": level,
            "parent": parent,
            "term": term,
        }
        response = self.session.get(url, params=params, headers=self.headers)
        if response.status_code != 200:
            raise Exception("Сессия недействительна или достигнут лимит запросов")
        json = response.json()
        if isinstance(json, dict) and json.get("success") == "false":
            return {}
        return {fias["value"]: fias["id"] for fias in json}

    def get_guids(self, params: dict):
        guids = dict()
        guids["region"], guids["region-guid"] = self.get_guid(ListFiasParser.Levels.REGION, parent="",
                                                              key=params.get("region"))
        guids["district"], guids["district-guid"] = self.get_guid(ListFiasParser.Levels.DISTRICT,
                                                                  parent=guids["region-guid"],
                                                                  key=params.get("district"))
        guids["settlement"], guids["settlement-guid"] = self.get_guid(ListFiasParser.Levels.SETTLEMENT,
                                                                      parent=guids["region-guid"],
                                                                      key=params.get("settlement"))
        guids["street"], guids["street-guid"] = self.get_guid(ListFiasParser.Levels.STREET,
                                                              parent=guids["settlement-guid"] or guids["region-guid"],
                                                              key=params.get("street"))
        guids["house"], guids["house-guid"] = self.get_guid(ListFiasParser.Levels.HOUSE, parent=guids["street-guid"],
                                                            key=params.get("house"))

        return guids

from address_parser import AddressParser, SimpleSearch
from models import SourceAddress, DestAddress, Address


class AddressParserAdapter(AddressParser):
    keys = {
        "Год ввода в эксплуатацию": "year",
        "Тип перекрытий": "overlap_material",
        "Материал несущих стен": "wall_material",
        "Количество этажей": "n_floors",
        "Последнее изменение анкеты": "last_changed",
        "Серия, тип постройки здания": "building_type",
        "Тип дома": "house_type",
        "Кадастровый номер": "cadastral_number",
    }

    def get_data(self, link):
        data = super().get_data(link)
        for key, value in AddressParserAdapter.keys.items():
            data[value] = data.pop(key)
        data["year"] = int(data.get("year") or 0)
        data["n_floors"] = int(data.get("n_floors") or 0)
        return data


class AddressService(Address):

    def __init__(self, parser, *args, **kwargs):
        self.parser = parser
        super().__init__(*args, **kwargs)

    def get_info(self) -> dict:
        if self.dest_id:
            return DestAddress.query.get(self.dest_id)
        self.n_tries += 1
        print(self.source_address)
        links = self.parser.search.search(self.source_address.region, self.source_address.city,
                                          self.source_address.street, self.source_address.house)
        for link in links:
            if not link.startswith("/myhouse"):
                continue
            return self.parser.get_data(link)
        else:
            print("ссылок не найдено")
        return {}

    def process(self):
        if self.dest_id:
            return
        if self.n_tries > 3:  # если более 3-х попыток, удаление из поиска
            Address.query.delete(address)
            Address.query.save()
        info = self.get_info()
        if not info:  # Если результат не найден, вернуть в поиск
            source_id = SourceAddress.query.insert(region=self.source_address.region,
                                                   kind_premises=self.source_address.kind_premises,
                                                   post_code=self.source_address.post_code,
                                                   type=self.source_address.type, city=self.source_address.city,
                                                   street_type=self.source_address.street_type,
                                                   street=self.source_address.street, house=self.source_address.house,
                                                   block=self.source_address.block,
                                                   flat=self.source_address.flat)
            SourceAddress.query.save()
            self.source_id = source_id
            Address.query.update(self)
            Address.query.save()
            return

        dest_id = DestAddress.query.insert(**info)
        DestAddress.query.save()
        self.dest_id = dest_id
        Address.query.update(self)
        Address.query.save()


if __name__ == "__main__":
    parser = AddressParserAdapter(SimpleSearch)
    for address_query in Address.query.all():
        address = AddressService(parser, address_query)
        address.process()

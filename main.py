from address_parser import AddressParser
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
        links = self.parser.simple_search(self.source_address.__str__())
        for link in links:
            if not link.startswith("/myhouse"):
                continue
            return self.parser.get_data(link)
        else:
            print("ссылок не найдено")
        return {}

    def process(self):
        if self.n_tries > 3 or self.dest_id:
            return
        info = self.get_info()
        if not info:
            return

        dest_id = DestAddress.query.insert(**info)
        DestAddress.query.save()
        self.dest_id = dest_id
        Address.query.update(self)
        Address.query.save()


# for _ in range(3):
#     parser = AddressParserAdapter()
#     for address_query in Address.query.all():
#         address = AddressService(parser, address_query)
#         address.process()
if __name__ == "__main__":
    parser = AddressParserAdapter()
    for address_query in Address.query.all():
        address = Address(address_query)
        links = parser.search.search(address.source_address.region, address.source_address.city,
                                     address.source_address.street,
                                     address.source_address.house)
        print(links)

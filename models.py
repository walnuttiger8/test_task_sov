import sqlite3
from pandas import read_excel

BASE_DB = "database.db"


class SourceAddressQuery:
    table_name = "source_address"

    def __init__(self, db_name: str = BASE_DB):
        self._connection = sqlite3.connect(db_name)
        self.cursor = self._connection.cursor()
        self._init_table()

    def save(self):
        self._connection.commit()

    def _init_table(self):
        self.cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {SourceAddressQuery.table_name}
        (id INTEGER PRIMARY KEY AUTOINCREMENT, kind_premises TEXT, post_code TEXT, region TEXT, type TEXT NULL, city TEXT NULL, street_type TEXT NULL,
        street TEXT NULL, house TEXT, block TEXT NULL, flat TEXT NULL) 
        """)
        self.save()

    def _drop(self):
        self.cursor.execute(f"""
        DROP TABLE {SourceAddressQuery.table_name}
        """)

    def insert(self, **kwargs):
        self.cursor.execute(f"""
            INSERT INTO {SourceAddressQuery.table_name} (kind_premises, post_code, region, type, city, street_type,
            street, house, block, flat) VALUES ('{kwargs.get("kind_premises") or ""}', '{kwargs.get("post_code") or ""}',
            '{kwargs.get("region") or ""}', '{kwargs.get("type") or ""}', '{kwargs.get("city") or ""}', '{kwargs.get("street_type") or ""}',
            '{kwargs.get("street") or ""}', '{kwargs.get("house") or ""}','{kwargs.get("block") or ""}', '{kwargs.get("flat") or ""}')
            """)
        return self.cursor.execute(f"SELECT last_insert_rowid()").fetchone()[0]

    def all(self):
        objects = self.cursor.execute(f"""
        SELECT * FROM {SourceAddressQuery.table_name}
        """).fetchall()
        return list(map(SourceAddress, objects))

    def get(self, id):
        return self.cursor.execute(f"""SELECT * FROM {SourceAddressQuery.table_name} WHERE id={id}""").fetchone()


class SourceAddress:
    query = SourceAddressQuery()
    _fields = ["id", "kind_premises", "post_code", "region", "type", "city", "street_type", "street", "house",
               "block",
               "flat"]
    __slots__ = _fields + ["address"]

    def _from_query(self, query):
        for key, value in zip(SourceAddress._fields, query):
            self.__setattr__(key, value)

    def __init__(self, query):
        self._from_query(query)
        if self.region.split():
            self.region = self.region.split()[0]

    def __str__(self):
        return " ".join(
            [self.__getattribute__(key) for key in ("region", "type", "city", "street_type", "street",
                                                    "house", "block",)])


class DestAddressQuery:
    table_name = "dest_address"

    def __init__(self, db_name: str = BASE_DB):
        self._connection = sqlite3.connect(db_name)
        self.cursor = self._connection.cursor()
        self._init_table()

    def save(self):
        self._connection.commit()

    def _init_table(self):
        self.cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {DestAddressQuery.table_name}
        (id INTEGER PRIMARY KEY AUTOINCREMENT, year DATE, n_floors INTEGER, last_changed DATE, building_type TEXT, house_type 
        TEXT, emergency BOOL, cadastral_number TEXT, overlap_type TEXT, wall_material TEXT)
        """)

    def _drop(self):
        self.cursor.execute(f"""
        DROP TABLE {DestAddressQuery.table_name} 
        """)

    def insert(self, **kwargs):
        year = kwargs.get("year") or ""
        n_floors = kwargs.get("n_floors") or ""
        last_changed = kwargs.get("last_changed") or ""
        building_type = kwargs.get("building_type") or ""
        house_type = kwargs.get("house_type") or ""
        emergency = kwargs.get("emergency") or ""
        cadastral_number = kwargs.get("cadastral_number") or ""
        overlap_type = kwargs.get("overlap_type") or ""
        wall_material = kwargs.get("wall_material") or ""
        self.cursor.execute(f"""
        INSERT INTO {DestAddressQuery.table_name} (year, n_floors, last_changed, building_type, house_type, emergency,
        cadastral_number, overlap_type, wall_material) VALUES ('{year}', '{n_floors}', '{last_changed}', '{building_type}', '{house_type}',
         '{emergency}', '{cadastral_number}', '{overlap_type}', '{wall_material}')
        """)
        return self.cursor.execute(f"SELECT last_insert_rowid()").fetchone()[0]

    def all(self):
        objects = self.cursor.execute(f"""
        SELECT * FROM {DestAddressQuery.table_name}
        """).fetchall()
        return list(map(DestAddress, objects))

    def get(self, id):
        if not id:
            return ()
        return self.cursor.execute(f"""SELECT * FROM {SourceAddressQuery.table_name} WHERE id={id}""").fetchone()


class DestAddress:
    query = DestAddressQuery()
    _fields = ["year", "n_floors", "last_changed", "building_type", "house_type", "emergency", "cadastral_number",
               "overlap_type", "wall_material"]
    __slots__ = _fields

    def __init__(self, query):
        self._from_query(query)

    def _from_query(self, query):
        for key, value in zip(DestAddress._fields, query):
            self.__setattr__(key, value)


class AddressQuery:
    table_name = "address"

    def __init__(self, db_name: str = BASE_DB):
        self._connection = sqlite3.connect(db_name)
        self.cursor = self._connection.cursor()
        self._init_table()

    def save(self):
        self._connection.commit()

    def _init_table(self):
        self.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {AddressQuery.table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            source_id INTEGER ,
            dest_id INTEGER NULL, 
            n_tries INTEGER DEFAULT(0),
            FOREIGN KEY (source_id) REFERENCES {SourceAddressQuery.table_name}(id) ON DELETE CASCADE
            FOREIGN KEY (dest_id) REFERENCES {DestAddressQuery.table_name}(id) ON DELETE CASCADE)
            """)

    def _drop(self):
        self.cursor.execute(f"""
            DROP TABLE {AddressQuery.table_name} 
            """)

    def insert(self, **kwargs):
        source_id = kwargs.get("source_id") or ''
        dest_id = kwargs.get("dest_id") or 'NULL'
        command = f"""
        INSERT INTO {AddressQuery.table_name} (source_id, dest_id) VALUES ({source_id}, {dest_id})
        """
        self.cursor.execute(command)
        return self.cursor.execute(f"SELECT last_insert_rowid()").fetchone()[0]

    def get(self, id):
        command = f"""SELECT * FROM {AddressQuery.table_name} WHERE id={id}"""
        query = self.cursor.execute(command).fetchone()
        return query

    def get_without_info(self):
        objects = self.all()
        return list(filter(lambda x: x[2] == None, objects))

    def get_with_info(self):
        objects = self.all()
        return list(filter(lambda x: x[2] != None, objects))

    def all(self):
        objects = self.cursor.execute(f"""
        SELECT * FROM {AddressQuery.table_name}
        """).fetchall()
        return objects

    def update(self, address):
        command = f"""
        UPDATE {AddressQuery.table_name}
        SET source_id = {address.source_id},
        dest_id = {address.dest_id},
        n_tries = {address.n_tries}
        WHERE id = {address.id}
        """
        return self.cursor.execute(command)


class Address:
    query = AddressQuery()
    _fields = ["id", "source_id", "dest_id", "n_tries"]
    __slots__ = _fields + ["source_address", "dest_address"]

    def __init__(self, query, *args, **kwargs):
        self.source_id = None
        self.dest_id = None
        self.n_tries = 0
        self._from_query(query)
        self.source_address = SourceAddress(SourceAddress.query.get(self.source_id))
        if self.dest_id:
            self.dest_address = DestAddress(DestAddress.query.get(self.dest_id))
        else:
            self.dest_address = None

    def _from_query(self, query):
        for key, value in zip(Address._fields, query):
            self.__setattr__(key, value)


def fill_db(filepath: str = "test_data.xlsx"):
    data = read_excel(filepath)
    data.fillna("")

    data.columns = ["kind_premises", "post_code", "region", "type", "city", "street_type", "street", "house", "block",
                    "flat", "address"]
    for index, row in data.iterrows():
        address = row.to_dict()
        address = {key: str(value).replace("nan", "") for key, value in address.items()}
        source_id = SourceAddress.query.insert(**address)
        SourceAddress.query.save()
        address_id = Address.query.insert(source_id=source_id)
        Address.query.save()


def drop_all():
    SourceAddress.query._drop()
    DestAddress.query._drop()
    Address.query._drop()



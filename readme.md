# Тестовое задание

В ходе выполнения тестового задания были реализованы следующие элементы:

- Парсинговый модуль для сбора информации со страницы дома
- Два метода поиска домов (простой и расширенный)
- база данных для хранения информации
- ORM обертка для базы данных 
- Все необходимые процедуры для анализа бд

## Структура проекта

Весь проект логически разделен на два модуля
- Парсинговый модуль
- Модуль БД

Весь функционал парсингового модуля инкапсулирован в класс _AdressParser_. Простой и расширенный поиск композиционно привязаны к классу _AddressParser_ в виде компонентов типа _Search_ (_SimpleSearch_ и _AdvancedSearch_ соответственно).

Для организации работы основного модуля реализованы классы _AddressParserAdapter_ и _AddressService_. 

_AddressParserAdapter_  преобразовывает данные в формат для записи в БД.
_AddressService_ представляет основной интерфейс взаимодействия парсера и БД

## Особенности реализации
### Поиск
Основной проблемой при осуществлении поиска (как расширенного, так и обычного) является лимитированное количество запросов и периодическое возникновение "капчи".
### Возможные решения
- при появлении "капчи" вводить ее вручную
- динамически менять ip-адресс при появлении "капчи"

### Расширенный поиск
При использовании расширенного поиска, для каждого поля поиска используется специальный guid-идентификатор. Идентификаторы можно получить последовательно отправляя GET-запросы на адрес _/list-fias_. В худшем случае, для получения guid-идентификаторов для всех полей поиска, может потребоваться в 5 раз больше запросов. 

Для осуществления расширенного поиска требуется иметь специальный _PHPSESSID_ с проверкой "на человека". _PHPSESSID_ который автоматически выдается при первом обращении не подходит для расширенного поиска.
### Возможные решения
- Отправлять запросы на _/list-fias_ с других ip-адресов для избежания блокировки. 
- Спарсить все возможные guid-идентификаторы с занесением в бд и вручную осуществлять поиск соответствующих guid-идентификаторов. (скопировать логику сервера)
- Вручную заходить на сайт для получения "человеческих" _PHPSESSID_ и самостоятельно вводить их в проектную конфигурацию (текущее решение). При таком подходе важно помнить, что "срок жизни" _PHPSESSID_ составляет порядка 1.5 - 2 дня

## Структура БД

База данных построена на sqlite3 и состоит из следующих таблиц:

- Таблица source_address - информация о параметрах поиска
- Таблица dest_address - результаты поиска
- Таблица address - связующая таблица представляющая логическую единицу БД

__При добавлении адреса__ в поиск (добавление в таблицу _souce_address_) создается соответствующая запись в таблице _adress_ которая содержит информацию о количестве попыток и результах поиска.
__При успешном поиске__, для соответствующей записи в таблице _adress_ создается ссылка на запись в таблице _dest_address_ с результатами поиска. Количество попыток поиска также соответственно увеличивается
__В противном случае__, как было указано в задании, в таблице _source_address_ создается новая запись с исходными данными поиска и меняется соответсвующая ссылка в таблице _address_.
__При превышении лимита__ в три попытки поиска, запись без результата поиска удаляется вместе с данными из таблицы с исходными данными для поиска.

## Установка

В требования проекта включен selenium как возможный источник для получения _PHPSESSID_

Установка необходимых библиотек

```sh
pip install -r requirements.txt
```


## Использование


Если вы хотите использовать расширенный поиск, то нужно указать _PHPSESSID_

/headers.py
```sh
headers["Cookie"] = "PHPSESSID=a5464b2a3b190484b41854dfe0585ca5"
```

При загрузке проекта база данных должна быть уже проинициализирована и заполнена.
Примечание: Таблицы инициализируются автоматически

Заполнение исходной таблицы данными с excel файла:
/models.py
```sh
fill_db()
```

Полный проход по исходной таблице поиска:
/main.py
```sh
parser = AddressParserAdapter(SimpleSearch)
    for address_query in Address.query.all():
        address = AddressService(parser, address_query)
        address.process()
```

Анализ результатов поиска:
/main.py
```sh
analysis()
```

Благодарю за потраченное время :)
from phpsessid import get_phpsessid

headers = dict()
headers[
    "Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;" \
                "q=0.8,application/signed-exchange;v=b3;q=0.9"
headers["Content-Type"] = "application/x-www-form-urlencoded"
headers["Host"] = "www.reformagkh.ru"
headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                        "Chrome/90.0.4430.216 YaBrowser/21.5.4.607 Yowser/2.5 Safari/537.36"
headers["Cookie"] = "PHPSESSID=7722c3ba2230b63f0e3f4d4633ff3ad3"

if __name__ == "__main__":
    print(get_phpsessid())

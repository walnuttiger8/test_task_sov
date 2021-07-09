from selenium import webdriver
from selenium.webdriver.firefox.options import Options


def get_phpsessid() -> {}:
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    driver.get("https://www.reformagkh.ru")
    cookies = driver.get_cookies()
    for cookie in cookies:
        if cookie["name"] == "PHPSESSID":
            return {cookie["name"]: cookie["value"]}

    return {}

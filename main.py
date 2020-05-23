import json
import os
import time

import dotenv
import requests
from bs4 import BeautifulSoup
from selenium import webdriver


ENDPOINT = 'https://store.nintendo.co.jp'

# dotenv.load_dotenv('.env')
ITEM_ID_LIST = os.environ.get('ITEM_ID_LIST').split(',')
SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')
# CHROMEDRIVER_PATH = os.environ.get('CHROMEDRIVER_PATH')


def get_item_page(item_id):
    options = webdriver.chrome.options.Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument('--proxy-server="direct://"')
    options.add_argument('--proxy-bypass-list=*')
    options.add_argument('--start-maximized')
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36')

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    # driver = webdriver.Chrome(CHROMEDRIVER_PATH, options=options)

    url = '{}/item/{}.html'.format(ENDPOINT, item_id)
    driver.get(url)
    html = driver.page_source.encode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')

    driver.quit()
    return soup


def is_on_sale(soup):
    cart_add_area = str(soup.find_all("div", class_="item-cart-add-area"))
    item_title = soup.find("h1", class_="item-title").get_text()
    on_sale = cart_add_area.find('カートに追加する') >= 0

    return item_title, on_sale


def post_slack(item_title):
    payload = {
        'username': 'My Nintendo Store 入荷通知',
        'attachments': [{
            'fallback': item_title,
            'color': '#D00000',
            'fields': [{
                'value': '「{}」が入荷しました'.format(item_title),
            }]
        }]
    }
    requests.post(SLACK_WEBHOOK_URL, data=json.dumps(payload))


if __name__ == '__main__':
    for item_id in ITEM_ID_LIST:
        print(get_item_page(item_id))
        item_title, on_sale = is_on_sale(get_item_page(item_id))
        if on_sale:
            post_slack(item_title)

        time.sleep(1)

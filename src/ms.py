from requests import post, get
from config import settings
from database import insert_items, create_tables
from models import ProductModel
from time import sleep
HEADERS = {"Authorization": f"Bearer {settings.MS_TOKEN}","Content-Type": "application/json", 'encoding': 'utf-8', "Accept-Encoding": "gzip"}


def get_all_items():
    url = "https://api.moysklad.ru/api/remap/1.2/entity/product"
    response = get(url=url, headers=HEADERS)
    if response.status_code == 200:
        data:list = response.json().get('rows', None)
        meta = response.json().get('meta', None)
        if meta:
            size = meta.get('size', None)
    if data:
        product_list = []
        for row in data:
            ms_code = row.get('code', '')
            name = row.get('name', '')
            currency = "THB"

            salePrices = row.get("salePrices", None)
            if salePrices:
                retail_price = salePrices[0].get("value", 0.0)/100
                mt10 = salePrices[1].get("value", 0.0)/100
                sale_price = salePrices[4].get("value", 0.0)/100
            else:
                retail_price = 0.0
                mt10 = 0.0

            attributes = row.get("attributes", None)
            if attributes:
                for attr in attributes:
                    if attr['id'] == 'a982acda-1d7f-11ee-0a80-0044001a10bf':
                        nicotine_strength = attr['value']
                    if attr['id'] == 'a982ae9d-1d7f-11ee-0a80-0044001a10c0':
                        taste = attr['value']
                    if attr['id'] == 'a982af52-1d7f-11ee-0a80-0044001a10c1':
                        snus_type = attr['value']
                    if attr['id'] == 'aef54879-1e61-11ee-0a80-0452002419cc':
                        brand = attr['value']
            else:
                nicotine_strength = ""
                taste = ""
                snus_type = ""
                brand = ""


            images = row.get("images", None)
            response = get(url=images['meta']['href'], headers=HEADERS).json()['rows']
            if response:
                with open(f'images/{ms_code}.png', "wb+") as file:
                    file.write(get(url = response[0]['meta']['downloadHref'], headers=HEADERS).content)
                image = f'{ms_code}.png'
            else:
                image = ''
            print(f'Downloaded - {ms_code} [{data.index(row)+1}/{size}]')
            sleep(1)
            product_list.append(ProductModel(
                ms_code = ms_code,
                name = name,
                retail_price = retail_price,
                image = image,
                mt10 = mt10,
                nicotine_strength = nicotine_strength,
                taste = taste,
                snus_type = snus_type,
                brand = brand,
                currency = currency,
                sale_price = sale_price,
                is_sale = bool(sale_price)
            ))
        insert_items(product_list)

def set_ms_webhook():
    url = "https://api.moysklad.ru/api/remap/1.2/entity/webhook"
    body = {
        "url": f'{settings.DOMAIN}/order/create/',
        "action": "CREATE",
        "entityType": 'customerorder'
    }
    post(url = url, headers=HEADERS, json = body)
    # body = {
    #     "url": f'{settings.DOMAIN}/create/',
    #     "action": "UPDATE",
    #     "entityType": 'customerorder'
    # }
    # post(url = url, headers=HEADERS, json = body)
    body = {
        "url": f'{settings.DOMAIN}/item/create/',
        "action": "CREATE",
        "entityType": 'product'
    }
    post(url = url, headers=HEADERS, json = body)
    body = {
        "url": f'{settings.DOMAIN}/item/edit/',
        "action": "UPDATE",
        "entityType": 'product'
    }
    post(url = url, headers=HEADERS, json = body)

def delete_ms_webhook():
    ...

if __name__ == "__main__":
    create_tables()
    get_all_items()
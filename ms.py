from requests import post, get
from db import add_item, edit_item
MY_STORAGE_TOKEN = 'ff19500f2665edf5c42a98d929e3a2230f065586'
HEADERS = {"Authorization": f"Bearer {MY_STORAGE_TOKEN}","Content-Type": "application/json", 'encoding': 'utf-8', "Accept-Encoding": "gzip"}


def get_all_items():
    url = "https://api.moysklad.ru/api/remap/1.2/entity/product"
    response = get(url=url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json().get('rows', None)
    if data:
        for row in data:
            ms_code = row.get('code', '')
            name = row.get('name', '').replace('/','').replace('"','')
            currency = "THB"
            salePrices = row.get("salePrices", None)
            retail_price = salePrices[0].get("value", 0.0)/100
            mt10=salePrices[1].get("value", 0.0)/100,
            mt30=salePrices[2].get("value", 0.0)/100,
            mt60=salePrices[3].get("value", 0.0)/100,
            mt120=salePrices[4].get("value", 0.0)/100,
            mt240=salePrices[5].get("value", 0.0)/100,
            productFolder = row.get("productFolder", None)
            if productFolder:
                category = get(url = productFolder['meta']['href'], headers=HEADERS).json().get("name", '')
            else:
                category = ''
            images = row.get("images", None)
            response = get(url=images['meta']['href'], headers=HEADERS).json()['rows']
            if response:
                with open(f'images/{ms_code}.png', "wb+") as file:
                    file.write(get(url = response[0]['meta']['downloadHref'], headers=HEADERS).content)
                image = f'{ms_code}.png'
            else:
                image = ''
            add_item((ms_code, name, retail_price, image, mt10, mt30, mt60, mt120, mt240, category, currency))
if __name__ == "__main__":
    get_all_items()
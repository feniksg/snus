from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from bot import Entrypoint, Entrypoint2
from typing import List
from config import settings
from models import ProductModel
from database import get_items, get_item, get_categories
from ms import set_ms_webhook, delete_ms_webhook
from time import sleep
import uvicorn, requests, os, sys


sys.path.insert(1, os.path.join(sys.path[0], '..'))

# TG Webhooks
delete_webhook = requests.get(f"https://api.telegram.org/bot{settings.BOT_TOKEN_1}/deleteWebhook?drop_pending_updates=True")
print(delete_webhook.status_code)
set_webhook = requests.get(f"https://api.telegram.org/bot{settings.BOT_TOKEN_1}/setWebhook?url={settings.DOMAIN}/api/bot/")
print(set_webhook.status_code)
delete_webhook2 = requests.get(f"https://api.telegram.org/bot{settings.BOT_TOKEN_2}/deleteWebhook?drop_pending_updates=True")
print(delete_webhook.status_code)
set_webhook2 = requests.get(f"https://api.telegram.org/bot{settings.BOT_TOKEN_2}/setWebhook?url={settings.DOMAIN}/api/bot2/")
print(set_webhook.status_code)
sleep(3)
# MS Webhooks
delete_ms_webhook()
set_ms_webhook()

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def run_entrypoint(body):
    Entrypoint(body, settings.BOT_TOKEN_1).run()

async def run_entrypoint2(body):
    Entrypoint2(body, settings.BOT_TOKEN_2).run()

async def run_entrypoint3(body):
    Entrypoint(body, settings.BOT_TOKEN_1).order_to_tg()

@app.post("/api/item/create/")
async def item_db_add(request: Request):
    body = await request.json()
    # print(body)
    return {"ok": True}

@app.post("/api/item/edit/")
async def item_db_edit(request: Request):
    body = await request.json()
    print(body)
    return {"ok": True}

@app.post("/api/order/create/")
async def handle_order_add(request: Request):
    return {"ok": True}

@app.get("/api/item/")
async def get_current_item(id = None):
    if id:
        item = get_item(int(id))
        return item
    else:
        return {"Error": "Indicate product id"}
    
@app.get("/api/data/")
async def get_db_data(brand = None, strength = None, taste = None, snus_type = None, search= None, is_sale = None):
    data = get_items(brand, strength, taste, snus_type, search, is_sale)
    data = [item.to_json() for item in data]
    return data

@app.get('/api/categories/')
async def get_cats(request: Request):
    cats = get_categories()
    return cats

@app.post('/api/tg/')
async def order_to_tg(request: Request, background_tasks: BackgroundTasks):
    body = await request.json()
    background_tasks.add_task(run_entrypoint3, body)
    return {"ok": True}

@app.post("/api/bot/")
async def main(request: Request, background_tasks: BackgroundTasks):
    body = await request.json()
    if body['message']:
        print(body['message']['date'])
    background_tasks.add_task(run_entrypoint, body)
    return {"ok": True}

@app.post("/api/bot2/")
async def main(request: Request, background_tasks: BackgroundTasks):
    body = await request.json()
    if body['message']:
        print(body['message']['date'])
    background_tasks.add_task(run_entrypoint2, body)
    return {"ok": True}

if __name__ == '__main__':
    uvicorn.run("server:app", host="0.0.0.0", port=4040, reload=True)
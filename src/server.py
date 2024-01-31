from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from bot import Entrypoint
from typing import List
from config import settings
from models import ProductModel
from database import get_items
from ms import set_ms_webhook, delete_ms_webhook
import uvicorn, requests, os, sys


sys.path.insert(1, os.path.join(sys.path[0], '..'))

#TG Webhooks
delete_webhook = requests.get(f"https://api.telegram.org/bot{settings.BOT_TOKEN_1}/deleteWebhook?drop_pending_updates=True")
set_webhook = requests.get(f"https://api.telegram.org/bot{settings.BOT_TOKEN_1}/setWebhook?url={settings.DOMAIN}")

#MS Webhooks
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

@app.post("/item/create/")
async def item_db_add(request: Request):
    body = await request.json()
    # print(body)
    return {"ok": True}

@app.post("/item/edit/")
async def item_db_edit(request: Request):
    body = await request.json()
    print(body)
    return {"ok": True}

@app.post("/order/create/")
async def handle_order_add(request: Request):
    return {"ok": True}


@app.get("/data/")
async def get_db_data(brand = None, nicotine_strength = None, taste = None, snus_type = None, search= None):
    data = get_items(brand, nicotine_strength, taste, snus_type, search)
    return data

@app.post("/bot/")
async def main(request: Request, background_tasks: BackgroundTasks):
    body = await request.json()
    print(body)
    background_tasks.add_task(run_entrypoint, body)
    return {"ok": True}

if __name__ == '__main__':
    uvicorn.run("server:app", host="0.0.0.0", port=4040, reload=True)
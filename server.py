from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from lib import Entrypoint
from linkhooks import link
from db import Product, get_data
from typing import List
import uvicorn 



app = FastAPI()
app.mount("/images", StaticFiles(directory="images"), name="images")

templates = Jinja2Templates(directory="templates")
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def run_entrypoint(body):
    Entrypoint(body).run()

@app.post("/item/create/")
async def item_db_add(request: Request):
    body = await request.json()
    print(body)
    return {"ok": True}

@app.post("/item/edit/")
async def item_db_edit(request: Request):
    body = await request.json()
    print(body)
    return {"ok": True}

@app.get("/data/", response_model=List[Product])
async def get_db_data(request: Request):
    data = get_data()
    return data

@app.get("/app/")
async def tgweb_app(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/bot/")
async def main(request: Request, background_tasks: BackgroundTasks):
    body = await request.json()
    print(body)
    background_tasks.add_task(run_entrypoint, body)
    return {"ok": True}

if __name__ == '__main__':
    link()
    uvicorn.run("server:app", host="0.0.0.0", port=4040, reload=True)
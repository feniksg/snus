import requests
from globals import TOKEN1, URL

def link():
    delete_webhook = requests.get(f"https://api.telegram.org/bot{TOKEN1}/deleteWebhook?drop_pending_updates=True")
    print('Старый Вебхук удалён')
    set_webhook = requests.get(f"https://api.telegram.org/bot{TOKEN1}/setWebhook?url={URL}")
    print('Новый Вебхук добавлен')
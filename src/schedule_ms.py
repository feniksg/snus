import threading, time, schedule
from ms import get_all_items

def updt(time_minutes):
    schedule.every(time_minutes).minutes.do(get_all_items)

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    download_products_thread = threading.Thread(target=updt, args=(30,))
    download_products_thread.start()

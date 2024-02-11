import threading, time, schedule
from ms import get_all_items

def updt(time_seconds):
    schedule.every(time_seconds).seconds.do(get_all_items)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    download_products_thread = threading.Thread(target=updt, args=(1800,))
    download_products_thread.start()

import psycopg2, requests
from pydantic import BaseModel

class Product(BaseModel):
    ms_code: str
    name: str
    retail_price: float
    image: str
    mt10: float
    mt30: float
    mt60: float
    mt120: float
    mt240: float
    category: str
    currency: str

conn = psycopg2.connect(host="localhost",
                        user="feniksg1",
                        password="adminADMIN",
                        port="5432",
                        database="tgsnus")

cursor = conn.cursor()

def delete_db():
    sql = "DROP TABLE item_list"

    cursor.execute(sql)
    conn.commit()

def create_db():
    alter_table_query = '''
        CREATE TABLE item_list (
    id SERIAL PRIMARY KEY,
    ms_code TEXT,
    name TEXT,
    retail_price FLOAT,
    image TEXT,
    price_more_than_10_items FLOAT,
    price_more_than_30_items FLOAT,
    price_more_than_60_items FLOAT,
    price_more_than_120_items FLOAT,
    price_more_than_240_items FLOAT,
    category TEXT,
    currency TEXT
    );
    '''

    cursor.execute(alter_table_query)
    conn.commit()

def delete_item(ms_code):
    delete_query = """
            DELETE FROM item_list
            WHERE ms_code = %s
        """
    cursor.execute(delete_query, (ms_code,))
    conn.commit()

def add_item(this_item):
    query = """SELECT ms_code FROM item_list;"""
    cursor.execute(query)
    codes = cursor.fetchall()
    codes = [code[0] for code in codes]
    if this_item[0] in codes:
        print('Error, item already exists.')
        edit_item(this_item)
    else:
        add_query = """
                INSERT INTO item_list (ms_code, name, retail_price, image,price_more_than_10_items, price_more_than_30_items, 
                    price_more_than_60_items, price_more_than_120_items, 
                    price_more_than_240_items, category, currency)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(add_query, this_item)
        conn.commit()

def edit_item(this_item):
    edit_query = """
            UPDATE item_list
            SET name = %s,
                retail_price = %s,
                image = %s,
                price_more_than_10_items = %s,
                price_more_than_30_items = %s,
                price_more_than_60_items = %s,
                price_more_than_120_items = %s,
                price_more_than_240_items = %s,
                category = %s,
                currency = %s
            WHERE ms_code = %s 
    """
    temp = [x for x in this_item[1:]]
    temp.append(this_item[0])
    temp = tuple(temp)
    cursor.execute(edit_query, temp)
    conn.commit()

def get_data():
    query = "SELECT * FROM item_list;"
    cursor.execute(query)
    result = cursor.fetchall()
    products = []
    for item in result:
        products.append(
            Product(ms_code=item[1],
                    name=item[2],
                    retail_price=item[3],
                    image=item[4],
                    mt10=item[5],
                    mt30=item[6],
                    mt60=item[7],
                    mt120=item[8],
                    mt240=item[9],
                    category=item[10],
                    currency=item[11])
        )
    return products

if __name__ == "__main__":
    # delete_db()
    # create_db()
    # print(get_data())
    ...

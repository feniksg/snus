from sqlalchemy import URL, text, create_engine
from sqlalchemy.orm import Session,sessionmaker
from config import settings
from models import AbstractModel, ProductModel
from typing import List

engine = create_engine(
    url = settings.DATABASE_URL_psycopg,
    echo=False
)

MySession = sessionmaker(engine, expire_on_commit=False)

session = MySession()

def check_connection():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT VERSION()"))
        print(f'{result.all()=}')

def create_tables():
    AbstractModel.metadata.drop_all(engine)
    AbstractModel.metadata.create_all(engine)

def insert_items(list:List[ProductModel]):
    try:
        for item in list:
            check = session.query(ProductModel).filter(ProductModel.ms_code == item.ms_code).all()
            if check:
                check = check[0]
                if check.name != item.name:
                    check.name = item.name
                if check.retail_price != item.retail_price:
                    check.retail_price = item.retail_price
                if check.mt10 != item.mt10:
                    check.mt10 = item.mt10
                if check.image != item.image:
                    check.image = item.image
                if check.nicotine_strength != item.nicotine_strength:
                    check.nicotine_strength = item.nicotine_strength
                if check.taste != item.taste:
                    check.taste = item.taste
                if check.snus_type != item.snus_type:
                    check.snus_type = item.snus_type
                if check.brand != item.brand:
                    check.brand = item.brand
                if check.currency != item.currency:
                    check.currency = item.currency
                if check.sale_price != item.sale_price:
                    check.sale_price = item.sale_price
                if check.is_sale != item.is_sale:
                    check.is_sale = item.is_sale
                if check.is_popular != item.is_popular:
                    check.is_popular = item.is_popular
                if check.search_name != item.search_name:
                    check.search_name = item.search_name
            else:
                session.add(item)
        session.commit()
    except Exception as e:
        session.rollback()
   
def get_item(id):
    item = session.query(ProductModel).filter(ProductModel.id == id).first()
    if item:
        return item
    else:
        return {"Error": "404. Item not found"}

def get_categories():
    all_brand = set([item[0] for item in session.query(ProductModel.brand).all()])
    if '' in all_brand:
        all_brand.remove('')
    all_taste = set([item[0] for item in session.query(ProductModel.taste).all()])
    if '' in all_taste:
        all_taste.remove('')
    all_nicotine_strength = set([item[0] for item in session.query(ProductModel.nicotine_strength).all()])
    if '' in all_nicotine_strength:
        all_nicotine_strength.remove('')
    return {
        'brands': sorted(list(all_brand)),
        'tasties': sorted(list(all_taste)),
        'strength': sorted(list(all_nicotine_strength))
    }

def get_items(brand = None, nicotine_strength = None, taste = None, snus_type = None, search:str= None, is_sale = None):
    all_items = session.query(ProductModel).filter(ProductModel.image != '')
    if brand:
        all_items = all_items.filter(ProductModel.brand == brand)
    if nicotine_strength:
        all_items = all_items.filter(ProductModel.nicotine_strength == float(nicotine_strength))
    if taste:
        all_items = all_items.filter(ProductModel.taste == taste)
    if snus_type:
        all_items = all_items.filter(ProductModel.snus_type == snus_type)
    if is_sale:
        is_sale = True if is_sale == 'True' or is_sale == 'true' else False
        all_items = all_items.filter(ProductModel.is_sale == is_sale)
    if search:
        all_items = all_items.filter(ProductModel.search_name.like(f'%{search.lower()}%'))
    return all_items.all()
    

          
if __name__ == '__main__':
    # insert_items([CategoryModel(name="Cat's and Crabs")])
    # insert_items([ProductModel(ms_code='00001',name='Тестовое  имя',retail_price= 200.0,image='00001.png', mt10= 180.0,nicotine_strength= 20.0, taste='MINT',snus_type= "1",brand= "1",currency= "THB",sale_price= 0,is_sale= False, is_popular=False, search_name= 'dsfsdf')])
    create_tables()
    # get_categories()
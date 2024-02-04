from sqlalchemy import URL, text, create_engine
from sqlalchemy.orm import Session,sessionmaker
from config import settings
from models import AbstractModel, ProductModel

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

def insert_items(list):
    for item in list:
        session.add(item)
    session.commit()

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

def get_items(brand = None, nicotine_strength = None, taste = None, snus_type = None, search= None, is_sale = None):
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
        all_items = all_items.filter(ProductModel.name.like(f'%{search}%'))
    return all_items.all()
    

          
if __name__ == '__main__':
    # insert_items([CategoryModel(name="Cat's and Crabs")])
    create_tables()
    # get_categories()
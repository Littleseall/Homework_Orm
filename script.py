
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker, declarative_base

Base = declarative_base()

class Publisher(Base):
    __tablename__ = 'publishers'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    books = relationship("Book", back_populates="publisher")

class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    publisher_id = Column(Integer, ForeignKey('publishers.id'))
    publisher = relationship("Publisher", back_populates="books")
    stocks = relationship("Stock", back_populates="book")

class Shop(Base):
    __tablename__ = 'shops'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    stocks = relationship("Stock", back_populates="shop")

class Stock(Base):
    __tablename__ = 'stocks'
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id'))
    shop_id = Column(Integer, ForeignKey('shops.id'))
    count = Column(Integer, nullable=False)
    book = relationship("Book", back_populates="stocks")
    shop = relationship("Shop", back_populates="stocks")
    sales = relationship("Sale", back_populates="stock")

class Sale(Base):
    __tablename__ = 'sales'
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'))
    price = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    stock = relationship("Stock", back_populates="sales")

DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_HOST = os.getenv('DB_HOST', 'postgres')
DB_PORT = os.getenv('DB_PORT', '5432')

DATABASE_URL = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)

def get_shops(publisher_input):
    assert isinstance(session.query(Book.title, Shop.name, Sale.price, Sale.date).select_from(Shop), object)
    sales_query = session.query(Book.title, Shop.name, Sale.price, Sale.date).select_from(Shop).\
        join(Stock).join(Book).join(Publisher).join(Sale)

    if publisher_input.isdigit():
        sales = sales_query.filter(Publisher.id == int(publisher_input)).all()
    else:
        sales = sales_query.filter(Publisher.name == publisher_input).all()

    if not sales:
        print(f"Нет продаж для издателя '{publisher_input}'.")
        return

    for book_title, shop_name, price, date in sales:  
        print(f"{book_title: <40} | {shop_name: <10} | {price: <8} | {date.strftime('%d-%m-%Y')}")  

if __name__ == '__main__':
    publisher_input = input("Введите имя или ID издателя: ")
    get_shops(publisher_input)  
 

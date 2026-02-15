from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Store(Base):
    __tablename__ = 'stores'
    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True)
    domain = Column(String)
    scanned_at = Column(DateTime, default=datetime.utcnow)

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey('stores.id'))
    name = Column(String)
    price = Column(Float)
    compare_at_price = Column(Float)
    variants_count = Column(Integer)
    product_type = Column(String)
    vendor = Column(String)
    created_at = Column(DateTime)
    tags = Column(Text)

class Metric(Base):
    __tablename__ = 'metrics'
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey('stores.id'))
    hero_score = Column(Float)
    discount_ratio = Column(Float) # New: % of catalog with discounts
    avg_variants = Column(Float)
    urgency = Column(Integer)
    bundle = Column(Integer)
    total_products = Column(Integer)
    avg_price = Column(Float)
    inventory_recency_days = Column(Integer) # New: Days since last launch
    vendor_count = Column(Integer) # New: To see Brand vs Reseller
    currency = Column(String) # NEW: Store currency
    theme = Column(String) # NEW: Detected theme name
    social_links = Column(Text) # NEW: JSON of social profiles
    pixels = Column(Text) # NEW: JSON of tracking pixels

class RawHTML(Base):
    __tablename__ = 'raw_html'
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey('stores.id'))
    path = Column(String)
    hash = Column(String)

def init_db(db_url="sqlite:///shopify_study/database.db"):
    # Delete old DB to avoid migration headache for this study
    import os
    if os.path.exists("shopify_study/database.db"):
        os.remove("shopify_study/database.db")
    
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)

def get_session(db_url="sqlite:///shopify_study/database.db"):
    engine = create_engine(db_url)
    return sessionmaker(bind=engine)()

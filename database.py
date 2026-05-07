import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, joinedload
from dotenv import load_dotenv

load_dotenv()

# Get DB URL from env, default to a local postgres if not provided
# Format: postgresql://user:password@localhost:5432/dbname
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/billing_manager")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    receipts = relationship("ReceiptDB", back_populates="user")

class ReceiptDB(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id")) # LINKED TO USER
    store_name = Column(String)
    store_address = Column(String)
    store_phone = Column(String)
    
    receipt_number = Column(String)
    date = Column(String)
    time = Column(String)
    cashier = Column(String)
    
    total = Column(Float)
    paid = Column(Float)
    change = Column(Float)
    num_items = Column(Integer)
    currency = Column(String)
    image_hash = Column(String, unique=True, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    raw_json = Column(JSON)

    user = relationship("UserDB", back_populates="receipts")
    items = relationship("ItemDB", back_populates="receipt", cascade="all, delete-orphan")

class ItemDB(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    receipt_id = Column(Integer, ForeignKey("receipts.id"))
    name = Column(String)
    quantity = Column(Integer)
    unit_price = Column(Float)
    total_price = Column(Float)
    currency = Column(String) # ADDED

    receipt = relationship("ReceiptDB", back_populates="items")

def init_db():
    Base.metadata.create_all(bind=engine)

def save_receipt(receipt_obj, user_id, image_hash=None):
    db = SessionLocal()
    try:
        new_receipt = ReceiptDB(
            user_id=user_id,
            store_name=receipt_obj.store_info.name,
            store_address=receipt_obj.store_info.address,
            store_phone=receipt_obj.store_info.phone,
            receipt_number=receipt_obj.receipt_info.receipt_number,
            date=receipt_obj.receipt_info.date,
            time=receipt_obj.receipt_info.time,
            cashier=receipt_obj.receipt_info.cachier,
            total=receipt_obj.totals.total,
            paid=receipt_obj.totals.paid,
            change=receipt_obj.totals.change,
            num_items=receipt_obj.totals.num_items,
            currency=receipt_obj.totals.currency,
            image_hash=image_hash,
            raw_json=receipt_obj.model_dump()
        )
        
        for item in receipt_obj.items:
            db_item = ItemDB(
                name=item.name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.total_price,
                currency=item.currency
            )
            new_receipt.items.append(db_item)
            
        db.add(new_receipt)
        db.commit()
        db.refresh(new_receipt)
        return new_receipt
    finally:
        db.close()

def get_receipt_by_hash(hash_str, user_id=None):
    db = SessionLocal()
    try:
        query = db.query(ReceiptDB).filter(ReceiptDB.image_hash == hash_str)
        if user_id:
            query = query.filter(ReceiptDB.user_id == user_id)
        return query.first()
    finally:
        db.close()

def get_recent_receipts(user_id, limit=8):
    db = SessionLocal()
    try:
        return db.query(ReceiptDB).options(joinedload(ReceiptDB.items)).filter(ReceiptDB.user_id == user_id).order_by(ReceiptDB.created_at.desc()).limit(limit).all()
    finally:
        db.close()

def get_all_receipts(user_id):
    db = SessionLocal()
    try:
        return db.query(ReceiptDB).options(joinedload(ReceiptDB.items)).filter(ReceiptDB.user_id == user_id).order_by(ReceiptDB.created_at.desc()).all()
    finally:
        db.close()

def delete_receipt(receipt_id, user_id):
    db = SessionLocal()
    try:
        receipt = db.query(ReceiptDB).filter(ReceiptDB.id == receipt_id, ReceiptDB.user_id == user_id).first()
        if receipt:
            db.delete(receipt)
            db.commit()
            return True
        return False
    finally:
        db.close()

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/billing_manager")

def migrate():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print("Starting migration...")
        
        # Add base_currency to users if not exists
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN base_currency VARCHAR DEFAULT 'USD'"))
            conn.commit()
            print("Added base_currency to users table.")
        except Exception as e:
            print(f"Note: base_currency might already exist in users: {e}")
            conn.rollback()

        # Add category to receipts if not exists
        try:
            conn.execute(text("ALTER TABLE receipts ADD COLUMN category VARCHAR"))
            conn.commit()
            print("Added category to receipts table.")
        except Exception as e:
            print(f"Note: category might already exist in receipts: {e}")
            conn.rollback()
            
        print("Migration complete.")

if __name__ == "__main__":
    migrate()

import hashlib
from sqlalchemy.orm import Session
from database import SessionLocal, UserDB

def hash_password(password: str) -> str:
    # Strip whitespace to prevent copy-paste errors
    return hashlib.sha256(password.strip().encode()).hexdigest()

def create_user(username, password):
    db = SessionLocal()
    try:
        # Normalize username to lowercase and strip whitespace
        username = username.strip().lower()
        if not username or not password:
            return None
            
        if db.query(UserDB).filter(UserDB.username == username).first():
            return None # User exists
            
        new_user = UserDB(username=username, password_hash=hash_password(password))
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        # Return a dict to avoid detachment issues in Streamlit
        return {"id": new_user.id, "username": new_user.username}
    finally:
        db.close()

def authenticate_user(username, password):
    db = SessionLocal()
    try:
        username = username.strip().lower()
        user = db.query(UserDB).filter(UserDB.username == username).first()
        if user and user.password_hash == hash_password(password):
            return {"id": user.id, "username": user.username}
        return None
    finally:
        db.close()

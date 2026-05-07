import bcrypt
import hashlib
from sqlalchemy.orm import Session
from database import SessionLocal, UserDB

def hash_password(password: str) -> str:
    # Strip whitespace and hash with bcrypt
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.strip().encode(), salt).decode()

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
        password = password.strip()
        user = db.query(UserDB).filter(UserDB.username == username).first()
        if not user:
            return None

        # Check if it's a legacy SHA-256 hash (64 chars hex)
        is_legacy = len(user.password_hash) == 64 and all(c in "0123456789abcdef" for c in user.password_hash)
        
        if is_legacy:
            legacy_hash = hashlib.sha256(password.encode()).hexdigest()
            if legacy_hash == user.password_hash:
                # MIGRATE TO BCRYPT
                user.password_hash = hash_password(password)
                db.commit()
                return {"id": user.id, "username": user.username}
            return None

        # Standard bcrypt check
        try:
            if bcrypt.checkpw(password.encode(), user.password_hash.encode()):
                return {"id": user.id, "username": user.username}
        except ValueError:
            return None # Still invalid salt/format
            
        return None
    finally:
        db.close()

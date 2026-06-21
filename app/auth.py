import base64
import hmac
import hashlib
import json
import time
import secrets
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import DB_User

SECRET_KEY = "memora-graph-system-key-change-in-production"
TOKEN_EXPIRY_SECONDS = 3600 * 24  # 1 day

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ==========================================
# Password Cryptography (PBKDF2)
# ==========================================

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"{salt}:{key.hex()}"

def verify_password(password: str, hashed_password: str) -> bool:
    try:
        salt, key_hex = hashed_password.split(':')
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return secrets.compare_digest(key.hex(), key_hex)
    except Exception:
        return False

# ==========================================
# Pure-Python JWT Generation & Validation
# ==========================================

def base64url_encode(payload: bytes) -> str:
    return base64.urlsafe_b64encode(payload).decode('utf-8').replace('=', '')

def base64url_decode(s: str) -> bytes:
    rem = len(s) % 4
    if rem > 0:
        s += '=' * (4 - rem)
    return base64.urlsafe_b64decode(s.encode('utf-8'))

def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = time.time() + TOKEN_EXPIRY_SECONDS
    
    header = {"alg": "HS256", "typ": "JWT"}
    header_enc = base64url_encode(json.dumps(header).encode('utf-8'))
    payload_enc = base64url_encode(json.dumps(payload).encode('utf-8'))
    
    signing_input = f"{header_enc}.{payload_enc}".encode('utf-8')
    signature = hmac.new(SECRET_KEY.encode('utf-8'), signing_input, hashlib.sha256).digest()
    sig_enc = base64url_encode(signature)
    
    return f"{header_enc}.{payload_enc}.{sig_enc}"

def verify_access_token(token: str) -> Optional[dict]:
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        header_enc, payload_enc, sig_enc = parts
        
        signing_input = f"{header_enc}.{payload_enc}".encode('utf-8')
        signature = hmac.new(SECRET_KEY.encode('utf-8'), signing_input, hashlib.sha256).digest()
        expected_sig = base64url_encode(signature)
        
        if not secrets.compare_digest(sig_enc, expected_sig):
            return None
            
        payload = json.loads(base64url_decode(payload_enc).decode('utf-8'))
        if "exp" in payload and payload["exp"] < time.time():
            return None
            
        return payload
    except Exception:
        return None

# ==========================================
# FastAPI Security Dependency
# ==========================================

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = verify_access_token(token)
    if payload is None:
        raise credentials_exception
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    user = db.query(DB_User).filter(DB_User.username == username).first()
    if user is None:
        raise credentials_exception
    return username

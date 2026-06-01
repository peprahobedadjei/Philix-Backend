import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv
import os


load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES =int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES",10080))

#Encoding password 
def hash_password(password:str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token (data:dict, expires_delta: Optional[timedelta] = None)-> str:
    to_encode=data.copy()
    expire =datetime.utcnow() +(expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv
import os
from jose import JWTError, jwt

from fastapi import Cookie, Depends, HTTPException, status
from requests import Session

from database import get_db
import models


load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES =int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES",10080))
SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM=os.getenv("ALGORITHM")

#Encoding password 
def hash_password(password:str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token (data:dict, expires_delta: Optional[timedelta] = None)-> str:
    to_encode=data.copy()
    expire =datetime.utcnow() +(expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode,SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token:str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
    except JWTError:
        return None

def get_current_user(
    access_token:Optional[str] =Cookie(default=None),
    db:Session=Depends(get_db)
)-> models.User:
    credentials_exception =HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="Not authenticated",
        headers={"WWW-Authenticate":"Bearer"},
    )

    if not access_token:
        raise credentials_exception
    
    payload=decode_token(access_token)
    if not payload:
        raise credentials_exception
    
    user_id =payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    user =db.query(models.User).filter(models.User.id == int(user_id)).first()
    if not user_id or not user.is_active:
        raise credentials_exception
    

    return user 


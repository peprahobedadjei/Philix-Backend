from fastapi import APIRouter,Response,Depends, HTTPException
from auth import create_access_token, hash_password, ACCESS_TOKEN_EXPIRE_MINUTES
import schemas
from sqlalchemy.orm import Session
from database import get_db
import models
from dotenv import load_dotenv
from datetime import timedelta
import os


load_dotenv()
IS_PRODUCTION =os.getenv("IS_PRODUCTION", "false").lower()=="true"

router =APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=schemas.TokenResponse, status_code=201)
def signup(body:schemas.SignupRequest, respose:Response, db:Session= Depends(get_db)):
    
    """"Register a new user. Credentials (Payload) sent in the request body"""
    if db.query(models.User).filter(models.User.email==body.email).first():
        raise HTTPException(status_code=400 , detail="Email already registered")
    if db.query(models.User).filter(models.User.username==body.username).first():
        raise HTTPException(status_code=400 , detail="Username already taken")
    

    user=models.User(
        email=body.email,
        username=body.username,
        full_name=body.full_name,
        hashed_password=hash_password(body.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token=create_access_token(
        data={"sub":str(user.id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) 
    )


    #Store JWT in an httpOnly cookies ; not local storage

    respose.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite='lax' ,#CSRF Protection
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES,
        secure=IS_PRODUCTION
    )

    return {"message":"Account created succesfully", "user":user}



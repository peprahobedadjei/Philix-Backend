from fastapi import APIRouter,Response,Depends, HTTPException
from auth import create_access_token, hash_password, ACCESS_TOKEN_EXPIRE_MINUTES, verify_password, get_current_user
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


@router.post("/login", response_model= schemas.TokenResponse)
def login (body:schemas.LoginRequest, response:Response, db:Session=Depends(get_db)):
    """"Login with email + Password in request body. JWT returned as httpOnly cookie"""
    user =db.query(models.User).filter(models.User.email==body.email).first()
    if not user or not verify_password (body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password ")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account deactivated")
    
    token=create_access_token(
        data={"sub":str(user.id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite='lax' ,#CSRF Protection
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES,
        secure=IS_PRODUCTION
    )
    return {"message":"Login Successful", "user":user}


@router.post("/logout", response_model= schemas.MessageResponse)
def logout(response:Response, current_user:models.User =Depends(get_current_user)):
    """"Clear the auth cookie to log out"""    
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=schemas.UserResponse)
def me(current_user:models.User=Depends(get_current_user)):
    return current_user

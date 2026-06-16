import os

from fastapi import Depends, HTTPException, Security
from sqlalchemy.orm import Session
from BetFanaticos_DBI.src.database import get_db
from BetFanaticos_DBI.src.models import DBUser
from BetFanaticos_DBI.src.authKey import api_key_header
from BetFanaticos_DBI.src.routers.auth import hash_password
import secrets

from dotenv import load_dotenv
load_dotenv()


# KI
# ChatGPT
# Prompt: Wie verteile ich Rollen in Fastapi?
def get_current_user(db: Session = Depends(get_db),api_key = Security(api_key_header)): #api_key_header wird aufgerufen
    if not api_key:
        raise HTTPException(status_code=401, detail="API Key fehlt")

    user = db.query(DBUser).filter(DBUser.api_key == api_key).first() # api key wird vom User aufgerugen,

    if not user :
        raise HTTPException(status_code=404, detail="API_Key stimmt nicht")

    return user


#KI
def require_admin(admin: DBUser = Depends(get_current_user)):
    if admin.role != "admin":    # rolle wird geprüft, falls kein admin, zugriff wird verweigert
        raise HTTPException(status_code=403,detail="Nur der Admin hat diese Berechtigung")
    return admin

def require_user(user: DBUser = Depends(get_current_user)):
    return user
#KI
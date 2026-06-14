from fastapi import Depends, HTTPException, Security
from sqlalchemy.orm import Session
from BetFanaticos_DBI.src.database import get_db
from BetFanaticos_DBI.src.models import DBUser
from BetFanaticos_DBI.src.authKey import api_key_header
import BetFanaticos_DBI.src.models as models


# KI
# ChatGPT
# Prompt: Wie verteile ich Rollen in Fastapi?
def get_current_user(db: Session = Depends(get_db),api_key = Security(api_key_header)): #api_key_header wird aufgerufen
    if not api_key:
        raise HTTPException(status_code=404, detail="API_Key wurde nicht gefunden")

    user = db.query(models.DBUser).filter(models.DBUser.api_key == api_key).first() # api key wird vom User aufgerugen,

    if not user :
        raise HTTPException(status_code=404, detail="API_Key stimmt nicht")


    return user

def require_admin(admin: DBUser = Depends(get_current_user)):
    if admin.role != "admin":    # rolle wird geprüft, falls kein admin, zugriff wird verweigert
        raise HTTPException(status_code=404,detail="Nur der Admin hat diese Berechtigung")
    return admin

def require_user(user: DBUser = Depends(get_current_user)):
    return user
#KI
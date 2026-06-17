from fastapi import Depends
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

import models
from database import get_db

# gibt an ,das im HTTP-Header nach einem feld mit diesem Namen gesucht wird
api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str=Security(api_key_header),  db: Session = Depends(get_db)):
    user = db.query(models.DBUser).filter(models.DBUser.api_key == api_key).first()

    if not user:
        raise HTTPException(status_code=401,detail="Invalid API Key")
    return user


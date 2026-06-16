from passlib.context import CryptContext
from fastapi import HTTPException
from fastapi import APIRouter, Depends
from fastapi_restful.cbv import cbv
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session
import secrets

from BetFanaticos_DBI.src.authKey import verify_api_key

from BetFanaticos_DBI.src import models
from BetFanaticos_DBI.src.database import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ChatGpt PROMPT : wie hasht man passwort in fastapi

def hash_password(password: str) -> str:
    """Erstellt aus einem Klartext-Passwort einen sicheren Hash."""

    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vergleicht ein Klartext-Passwort mit einem gespeicherten Hash."""
    return pwd_context.verify(plain_password, hashed_password)


class UserCreate(BaseModel):
    name: str
    password : str

    @field_validator("name")
    @classmethod
    def check_name_length(cls, value: str):
        if not value.strip():
            raise ValueError("Bitte geben Sie einen Namen ein.")
        if len(value) > 20:
            raise ValueError("Name darf maximal 20 Zeichen haben.")
        return value

    @field_validator("password")
    @classmethod
    def check_password_length(cls, value: str):
        if not value.strip():
            raise ValueError("Bitte geben Sie ein Passwort ein.")
        if len(value) < 3 or len(value) > 8:
            raise ValueError("Passwort muss zwischen 3 und 8 Zeichen lang sein.")
        return value


class UserResponse(BaseModel):
    userId: int
    name : str

class LoginRequest(BaseModel):
    name: str
    password : str

    class Config:
        from_attributes = True


@cbv(router)
class UserAPI:

    db: Session = Depends(get_db)


    @router.get("/me", response_model=UserResponse)
    def get_user(user: models.DBUser = Depends(verify_api_key)):
        return user

    @router.post("/register", response_model=UserResponse)
    def register_user(self, user_data: UserCreate):

        user = self.db.query(models.DBUser).filter(models.DBUser.name == user_data.name).first()

        if user:
            raise HTTPException(status_code=400, detail="User existiert bereits")

        hashed_pwd = hash_password(user_data.password)
        api_key = secrets.token_hex(32)

        new_user = models.DBUser(
            name=user_data.name,
            password=hashed_pwd,
            api_key=api_key
        )

        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)

        return new_user

    @router.post("/login")
    def login(self, request: LoginRequest):

        user = self.db.query(models.DBUser).filter(models.DBUser.name == request.name).first()

        if user is None:
            raise HTTPException(status_code=404, detail="User wurde nicht gefunden")

        if not verify_password(request.password, user.password):
            raise HTTPException(status_code=401, detail="Falsches Passwort")

        return {"api_key": user.api_key,
                "user": {
                "userId": user.userId,
                "name": user.name,
                "role": user.role }
        }
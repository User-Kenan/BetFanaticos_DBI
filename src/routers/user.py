from dbm import error
from http.client import HTTPException
from os import name

from fastapi import APIRouter
from fastapi.params import Depends
from fastapi_restful.cbv import cbv
from pydantic import BaseModel
from sqlalchemy.orm import query
from starlette.middleware.sessions import Session

from src import models
from src.database import get_db

router = APIRouter(prefix="/user", tags=["User"])

class UserCreate(BaseModel):
    name: str
    password: int

class UserResponse(UserCreate):
    id: int

    class Config:
        from_attributes = True


@cbv(router)
class UserAPI:

    db: Session = Depends(get_db)

    def get_or_404(self, user_id: int):
        user = self.db.query(models.DBUser).filter(models.DBUser.userId == user_id).first()

        if user is None:
            raise HTTPException(status_code=404, detail="User nicht gefunden")

        return user

    @router.get("/", response_model=list[UserResponse])
    def get_all_users(self):
        return self.db.query(models.DBUser).all()

    @router.get("/{user_id}", response_model=UserResponse)
    def get_user(self, user_id: int):
        return self.get_or_404(user_id)

    @router.post("/", response_model=UserResponse)
    def create_user(self, user: UserCreate):
        db_user = models.DBUser(
            name=user.name,
            password=user.password
        )

        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)

        return db_user

    @router.put("/{user_id}", response_model=UserResponse)
    def update_user(self, user_id: int, user: UserCreate):
        db_user = self.get_or_404(user_id)

        db_user.name = user.name
        db_user.password = user.password

        self.db.commit()
        self.db.refresh(db_user)

        return db_user

    @router.delete("/{user_id}")
    def delete_user(self, user_id: int):
        db_user = self.get_or_404(user_id)

        self.db.delete(db_user)
        self.db.commit()

        return {"message": "User gelöscht"}
from BetFanaticos_DBI.src import models
from BetFanaticos_DBI.src.database import get_db
from BetFanaticos_DBI.src.models import DBUser
from BetFanaticos_DBI.src.permission import require_admin
from BetFanaticos_DBI.src.routers.auth import UserResponse, UserCreate
from BetFanaticos_DBI.src.routers.auth import hash_password
from fastapi import APIRouter, Depends, HTTPException
from fastapi_restful.cbv import cbv
from sqlalchemy.orm import Session

router = APIRouter(prefix="/admin", tags=["Adm"])

class AdminUpdate(UserCreate):
    role: str


@cbv(router)
class UserAPI:

    db: Session = Depends(get_db)

    def get_or_404(self, user_id: int):
        user = self.db.query(models.DBUser).filter(
            models.DBUser.userId == user_id
        ).first()

        if user is None:
            raise HTTPException(status_code=404, detail="User wurde nicht gefunden")

        return user

    @router.get("/users", response_model=list[UserResponse])
    def get_users(self,admin: DBUser = Depends(require_admin)):
        return self.db.query(DBUser).all()

    @router.get("/users/{user_id}", response_model=UserResponse)
    def get_betitem(self, user_id: int,admin: DBUser = Depends(require_admin)):
        return self.get_or_404(user_id)

    @router.delete("/users/{user_id}")
    def delete(self, user_id: int,admin: DBUser = Depends(require_admin)):
        user = self.get_or_404(user_id)

        self.db.delete(user)
        self.db.commit()
        return {"message": "Eintrag gelöscht"}

    @router.put("/users/{user_id}", response_model=UserResponse)
    def update_user(
            self,
            user_id: int,
            u_user: AdminUpdate,
            admin: DBUser = Depends(require_admin)
    ):

        user = self.get_or_404(user_id)

        user.name = u_user.name
        user.password = hash_password(u_user.password)
        user.role =  u_user.role

        self.db.commit()
        self.db.refresh(user)

        return user

    @router.post("/users", response_model=UserResponse)
    def create_user(self, user_data: UserCreate, admin: DBUser = Depends(require_admin)):

        new_user = DBUser(
            name=user_data.name,
            password=hash_password(user_data.password),
            role="user"
        )

        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)

        return new_user


    # KI
    # Chatgpt
    # Prompt: Woher weiß aber programm ob ich Admin bin

    @router.post("/admin/users/{user_id}/make-admin")
    def make_admin(self,user_id: int, admin: DBUser = Depends(require_admin)):

        user = self.db.query(models.DBUser).filter(models.DBUser.userId == user_id).first()

        if not user:
            raise HTTPException(404)

        user.role = "admin"
        self.db.commit()

        return {"message": "User ist jetzt Admin"}

    #Ki

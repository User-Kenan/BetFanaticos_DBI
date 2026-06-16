from fastapi import APIRouter, Depends, HTTPException
from fastapi_restful.cbv import cbv
from sqlalchemy.orm import Session

from BetFanaticos_DBI.src.routers.auth import UserResponse

from BetFanaticos_DBI.src import models
from BetFanaticos_DBI.src.database import get_db


router = APIRouter(prefix="/user", tags=["User"])

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

    @router.get("/users/{user_id}", response_model=UserResponse)
    def get_betitem(self, user_id: int):
        return self.get_or_404(user_id)

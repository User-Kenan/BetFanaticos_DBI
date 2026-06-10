from fastapi import APIRouter, Depends, HTTPException
from fastapi_restful.cbv import cbv
from pydantic import BaseModel
from sqlalchemy.orm import Session

from BetFanaticos_DBI.src import models
from BetFanaticos_DBI.src.database import get_db

router = APIRouter(prefix="/sidequest", tags=["Sidequest"])


class SidequestCreate(BaseModel):
    challange: str
    start_date: str
    end_date: str
    earned_coins: int


class SidequestResponse(SidequestCreate):
    side_quest_id: int

    class Config:
        from_attributes = True


@cbv(router)
class SidequestAPI:

    db: Session = Depends(get_db)

    def get_or_404(self, side_quest_id: int):
        sidequest = self.db.query(models.DBSidequest).filter(
            models.DBSidequest.side_quest_id == side_quest_id
        ).first()

        if sidequest is None:
            raise HTTPException(status_code=404, detail="Sidequest nicht gefunden")

        return sidequest

    @router.get("/", response_model=list[SidequestResponse])
    def get_all_sidequests(self):
        return self.db.query(models.DBSidequest).all()

    @router.get("/{side_quest_id}", response_model=SidequestResponse)
    def get_sidequest(self, side_quest_id: int):
        return self.get_or_404(side_quest_id)

    @router.post("/", response_model=SidequestResponse)
    def create_sidequest(self, sidequest: SidequestCreate):
        db_sidequest = models.DBSidequest(
            challange=sidequest.challange,
            start_date=sidequest.start_date,
            end_date=sidequest.end_date,
            earned_coins=sidequest.earned_coins
        )

        self.db.add(db_sidequest)
        self.db.commit()
        self.db.refresh(db_sidequest)

        return db_sidequest

    @router.put("/{side_quest_id}", response_model=SidequestResponse)
    def update_sidequest(self, side_quest_id: int, sidequest: SidequestCreate):
        db_sidequest = self.get_or_404(side_quest_id)

        db_sidequest.challange = sidequest.challange
        db_sidequest.start_date = sidequest.start_date
        db_sidequest.end_date = sidequest.end_date
        db_sidequest.earned_coins = sidequest.earned_coins

        self.db.commit()
        self.db.refresh(db_sidequest)

        return db_sidequest

    @router.delete("/{side_quest_id}")
    def delete_sidequest(self, side_quest_id: int):
        db_sidequest = self.get_or_404(side_quest_id)

        self.db.delete(db_sidequest)
        self.db.commit()

        return {"message": "Sidequest gelöscht"}
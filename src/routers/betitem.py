import models
from database import get_db

from fastapi import APIRouter, Depends, HTTPException
from fastapi_restful.cbv import cbv
from pydantic import BaseModel
from sqlalchemy.orm import Session

router = APIRouter(prefix="/betitem", tags=["Betitem"])


class BetitemCreate(BaseModel):
    score_team_a: int
    score_team_b: int
    bet_money: float
    status: str
    bet_type: str
    prediction: str
    odds: float
    home_team: str
    away_team: str
    bet_id: int
    match_id: int


class BetitemResponse(BetitemCreate):
    bet_item_id: int

    class Config:
        from_attributes = True


@cbv(router)
class BetitemAPI:

    db: Session = Depends(get_db)

    def get_or_404(self, bet_item_id: int):
        betitem = self.db.query(models.DBBetitem).filter(
            models.DBBetitem.bet_item_id == bet_item_id
        ).first()

        if betitem is None:
            raise HTTPException(status_code=404, detail="Betitem nicht gefunden")

        return betitem

    @router.get("/", response_model=list[BetitemResponse])
    def get_all_betitems(self):
        return self.db.query(models.DBBetitem).all()



    @router.get("/open/{user_id}", response_model=list[BetitemResponse])
    def get_open_betitems_by_user(self, user_id: int):
        return (
            self.db.query(models.DBBetitem)
            .join(models.DBBet, models.DBBet.bet_id == models.DBBetitem.bet_id)
            .filter(models.DBBet.user_id == user_id)
            .filter(models.DBBetitem.status == "Open")
            .all()
        )

    @router.get("/{bet_item_id}", response_model=BetitemResponse)
    def get_betitem(self, bet_item_id: int):
        return self.get_or_404(bet_item_id)

    @router.post("/", response_model=BetitemResponse)
    def create_betitem(self, betitem: BetitemCreate):
        db_betitem = models.DBBetitem(
            score_team_a=betitem.score_team_a,
            score_team_b=betitem.score_team_b,
            bet_money=betitem.bet_money,
            status=betitem.status,
            bet_type=betitem.bet_type,
            prediction=betitem.prediction,
            odds=betitem.odds,
            home_team=betitem.home_team,
            away_team=betitem.away_team,
            bet_id=betitem.bet_id,
            match_id=betitem.match_id
        )

        self.db.add(db_betitem)
        self.db.commit()
        self.db.refresh(db_betitem)

        return db_betitem

    @router.put("/{bet_item_id}", response_model=BetitemResponse)
    def update_betitem(self, bet_item_id: int, betitem: BetitemCreate):
        db_betitem = self.get_or_404(bet_item_id)

        db_betitem.score_team_a = betitem.score_team_a
        db_betitem.score_team_b = betitem.score_team_b
        db_betitem.bet_money = betitem.bet_money
        db_betitem.status = betitem.status
        db_betitem.bet_type = betitem.bet_type
        db_betitem.prediction = betitem.prediction
        db_betitem.odds = betitem.odds
        db_betitem.home_team = betitem.home_team
        db_betitem.away_team = betitem.away_team
        db_betitem.bet_id = betitem.bet_id
        db_betitem.match_id = betitem.match_id

        self.db.commit()
        self.db.refresh(db_betitem)

        return db_betitem

    @router.delete("/{bet_item_id}")
    def delete_betitem(self, bet_item_id: int):
        db_betitem = self.get_or_404(bet_item_id)

        self.db.delete(db_betitem)
        self.db.commit()

        return {"message": "Betitem gelöscht"}
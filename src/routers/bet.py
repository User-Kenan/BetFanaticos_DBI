from fastapi import APIRouter, Depends, HTTPException
from fastapi_restful.cbv import cbv
from pydantic import BaseModel
from sqlalchemy.orm import Session

from BetFanaticos_DBI.src import models
from BetFanaticos_DBI.src.database import get_db

router = APIRouter(prefix="/bet", tags=["Bet"])


class BetCreate(BaseModel):
    status: str
    user_id: int


class BetResponse(BetCreate):
    bet_id: int

    class Config:
        from_attributes = True


@cbv(router)
class BetAPI:

    db: Session = Depends(get_db)

    def get_or_404(self, bet_id: int):
        bet = self.db.query(models.DBBet).filter(
            models.DBBet.bet_id == bet_id
        ).first()

        if bet is None:
            raise HTTPException(status_code=404, detail="Wette nicht gefunden")

        return bet

    @router.get("/", response_model=list[BetResponse])
    def get_all_bets(self):
        return self.db.query(models.DBBet).all()

    @router.get("/{bet_id}", response_model=BetResponse)
    def get_bet(self, bet_id: int):
        return self.get_or_404(bet_id)

    @router.post("/", response_model=BetResponse)
    def create_bet(self, bet: BetCreate):
        db_bet = models.DBBet(
            status=bet.status,
            user_id=bet.user_id
        )

        self.db.add(db_bet)
        self.db.commit()
        self.db.refresh(db_bet)

        return db_bet

    @router.put("/{bet_id}", response_model=BetResponse)
    def update_bet(self, bet_id: int, bet: BetCreate):
        db_bet = self.get_or_404(bet_id)

        db_bet.status = bet.status
        db_bet.user_id = bet.user_id

        self.db.commit()
        self.db.refresh(db_bet)

        return db_bet

    @router.delete("/{bet_id}")
    def delete_bet(self, bet_id: int):
        db_bet = self.get_or_404(bet_id)

        self.db.delete(db_bet)
        self.db.commit()

        return {"message": "Wette gelöscht"}
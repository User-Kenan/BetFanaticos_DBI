import BetFanaticos_DBI.src.models as models
from BetFanaticos_DBI.src.database import get_db

from fastapi import APIRouter, Depends, HTTPException
from fastapi_restful.cbv import cbv
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional


router = APIRouter(prefix="/bet", tags=["Bet"])


class BetCreate(BaseModel):
    user_id: int
    match_id: int
    amount: float
    prediction: str
    odds: float


class BetResponse(BaseModel):
    bet_id: int
    status: str
    user_id: int
    bet_item_id: Optional[int] = None

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

    @router.get("/")
    def get_all_bets(self):
        return self.db.query(models.DBBet).all()

    @router.get("/{bet_id}")
    def get_bet(self, bet_id: int):
        return self.get_or_404(bet_id)

    @router.post("/create", response_model=BetResponse)
    def create_bet(self, bet: BetCreate):
        wallet = self.db.query(models.DBWallet).filter(
            models.DBWallet.user_id == bet.user_id
        ).first()

        if wallet is None:
            wallet = models.DBWallet(
                user_id=bet.user_id,
                coins=1000
            )
            self.db.add(wallet)
            self.db.flush()

        if wallet.coins < bet.amount:
            raise HTTPException(
                status_code=400,
                detail="Du hast nicht genug Coins"
            )

        wallet.coins -= bet.amount

        db_bet = models.DBBet(
            status="open",
            user_id=bet.user_id
        )

        self.db.add(db_bet)
        self.db.flush()

        db_betitem = models.DBBetitem(
            score_team_a=0,
            score_team_b=0,
            bet_money=bet.amount,
            status="open",
            bet_type=bet.prediction,
            bet_id=db_bet.bet_id,
            match_id=bet.match_id
        )

        self.db.add(db_betitem)

        self.db.commit()
        self.db.refresh(db_bet)
        self.db.refresh(db_betitem)

        return {
            "bet_id": db_bet.bet_id,
            "status": db_bet.status,
            "user_id": db_bet.user_id,
            "bet_item_id": db_betitem.bet_item_id
        }


    @router.delete("/{bet_id}")
    def delete_bet(self, bet_id: int):
        db_bet = self.get_or_404(bet_id)

        self.db.delete(db_bet)
        self.db.commit()

        return {"message": "Wette gelöscht"}
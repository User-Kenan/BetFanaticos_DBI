import BetFanaticos_DBI.src.models as models
from BetFanaticos_DBI.src.database import get_db

from fastapi import APIRouter, Depends, HTTPException
from fastapi_restful.cbv import cbv
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session
from typing import Optional
import logging

logger = logging.getLogger("betfanaticos.bet")


router = APIRouter(prefix="/bet", tags=["Bet"])


class BetCreate(BaseModel):
    user_id: int
    match_id: int
    amount: float
    prediction: str
    odds: float

    @field_validator("user_id", "match_id")
    @classmethod
    def ids_must_be_positive(cls, value: int):
        if value <= 0:
            raise ValueError("ID muss größer als 0 sein")
        return value

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, value: float):
        if value <= 0:
            raise ValueError("Der Einsatz muss größer als 0 sein")
        return value

    @field_validator("odds")
    @classmethod
    def odds_must_be_valid(cls, value: float):
        if value < 1:
            raise ValueError("Die Quote muss mindestens 1 sein")
        return value

    @field_validator("prediction")
    @classmethod
    def prediction_must_be_valid(cls, value: str):
        value = value.lower().strip()
        allowed = [
            "home", "heim", "heimsieg", "1",
            "away", "auswaerts", "auswärts", "auswaertssieg", "auswärtssieg", "2",
            "draw", "x", "unentschieden", "remis"
        ]

        if value not in allowed:
            raise ValueError("prediction muss home, away oder draw sein")

        return value


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
        user = self.db.query(models.DBUser).filter(
            models.DBUser.userId == bet.user_id
        ).first()

        if user is None:
            logger.warning("Wette abgelehnt: user_id=%s existiert nicht", bet.user_id)
            raise HTTPException(status_code=404, detail="User nicht gefunden")

        match = self.db.query(models.DBMatch).filter(
            models.DBMatch.match_id == bet.match_id
        ).first()

        if match is None:
            logger.warning("Wette abgelehnt: match_id=%s existiert nicht", bet.match_id)
            raise HTTPException(status_code=404, detail="Match nicht gefunden")

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
            logger.info("Wallet automatisch erstellt für user_id=%s", bet.user_id)

        if wallet.coins < bet.amount:
            logger.warning(
                "Wette abgelehnt: user_id=%s, coins=%s, amount=%s",
                bet.user_id,
                wallet.coins,
                bet.amount
            )
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


        db_betitem=models.DBBetitem(
            bet_id=db_bet.bet_id,
            match_id=bet.match_id,
            bet_money=bet.amount,
            status="open",
            bet_type="winner",
            prediction=bet.prediction,
            odds=bet.odds
        )


        self.db.add(db_betitem)

        # Statistics-Zeile direkt anlegen/aktualisieren, damit bet_count nach POST /bet stimmt.
        statistics = self.db.query(models.DBStatistics).filter(
            models.DBStatistics.user_id == bet.user_id
        ).first()

        if statistics is None:
            statistics = models.DBStatistics(
                user_id=bet.user_id,
                bet_count=1,
                bet_won=0,
                bet_lost=0,
                win_rate=0,
                profit=0,
                biggest_win=0,
                biggest_lost=0
            )
            self.db.add(statistics)
        else:
            statistics.bet_count = (statistics.bet_count or 0) + 1

        self.db.commit()
        self.db.refresh(db_bet)
        self.db.refresh(db_betitem)

        logger.info(
            "Wette erstellt: bet_id=%s, bet_item_id=%s, user_id=%s, match_id=%s, amount=%s, prediction=%s",
            db_bet.bet_id,
            db_betitem.bet_item_id,
            bet.user_id,
            bet.match_id,
            bet.amount,
            bet.prediction
        )

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
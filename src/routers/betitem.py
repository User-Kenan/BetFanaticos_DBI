import logging
from typing import Literal

import BetFanaticos_DBI.src.models as models
from BetFanaticos_DBI.src.database import get_db

from fastapi import APIRouter, Depends, HTTPException
from fastapi_restful.cbv import cbv
from pydantic import BaseModel, field_validator, ConfigDict
from sqlalchemy.orm import Session


logger = logging.getLogger("betfanaticos.betitem")


router = APIRouter(prefix="/betitem", tags=["Betitem"])


class BetitemCreate(BaseModel):
    bet_id: int
    match_id: int
    bet_money: float
    status: Literal["open", "won", "lost"] = "open"
    bet_type: str = "winner"
    prediction: Literal["home", "away", "draw"]
    odds: float

    @field_validator("bet_id", "match_id")
    @classmethod
    def id_must_be_positive(cls, value):
        if value <= 0:
            raise ValueError("ID muss größer als 0 sein")
        return value

    @field_validator("bet_money")
    @classmethod
    def bet_money_must_be_positive(cls, value):
        if value <= 0:
            raise ValueError("Einsatz muss größer als 0 sein")
        return value

    @field_validator("odds")
    @classmethod
    def odds_must_be_valid(cls, value):
        if value < 1:
            raise ValueError("Quote muss mindestens 1 sein")
        return value

    @field_validator("bet_type")
    @classmethod
    def bet_type_must_not_be_empty(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Bet-Type darf nicht leer sein")

        return value

    @field_validator("prediction", mode="before")
    @classmethod
    def normalize_prediction(cls, value):
        if value is None:
            raise ValueError("Prediction darf nicht leer sein")

        value = str(value).lower().strip()

        if value in ["1", "heim", "heimsieg"]:
            return "home"

        if value in ["2", "auswärts", "auswaerts", "auswärtssieg", "auswaertssieg"]:
            return "away"

        if value in ["x", "unentschieden"]:
            return "draw"

        if value not in ["home", "away", "draw"]:
            raise ValueError("Prediction muss home, away oder draw sein")

        return value


class BetitemResponse(BaseModel):
    bet_item_id: int
    bet_id: int
    match_id: int
    bet_money: float
    status: str
    bet_type: str
    prediction: str
    odds: float

    model_config = ConfigDict(from_attributes=True)


@cbv(router)
class BetitemAPI:

    db: Session = Depends(get_db)

    def get_or_404(self, bet_item_id: int):
        betitem = (
            self.db.query(models.DBBetitem)
            .filter(models.DBBetitem.bet_item_id == bet_item_id)
            .first()
        )

        if betitem is None:
            logger.warning(f"Betitem mit ID {bet_item_id} wurde nicht gefunden.")
            raise HTTPException(status_code=404, detail="Betitem nicht gefunden")

        return betitem

    def check_bet_exists(self, bet_id: int):
        bet = (
            self.db.query(models.DBBet)
            .filter(models.DBBet.bet_id == bet_id)
            .first()
        )

        if bet is None:
            logger.warning(f"Bet mit ID {bet_id} wurde nicht gefunden.")
            raise HTTPException(status_code=404, detail="Bet nicht gefunden")

        return bet

    def check_match_exists(self, match_id: int):
        match = (
            self.db.query(models.DBMatch)
            .filter(models.DBMatch.match_id == match_id)
            .first()
        )

        if match is None:
            logger.warning(f"Match mit ID {match_id} wurde nicht gefunden.")
            raise HTTPException(status_code=404, detail="Match nicht gefunden")

        return match

    @router.get("/", response_model=list[BetitemResponse])
    def get_all_betitems(self):
        logger.info("Alle Betitems wurden abgefragt.")
        return self.db.query(models.DBBetitem).all()

    @router.get("/open/{user_id}", response_model=list[BetitemResponse])
    def get_open_betitems_by_user(self, user_id: int):
        logger.info(f"Offene Betitems für User {user_id} wurden abgefragt.")

        return (
            self.db.query(models.DBBetitem)
            .join(models.DBBet, models.DBBet.bet_id == models.DBBetitem.bet_id)
            .filter(models.DBBet.user_id == user_id)
            .filter(models.DBBetitem.status == "open")
            .all()
        )

    @router.get("/{bet_item_id}", response_model=BetitemResponse)
    def get_betitem(self, bet_item_id: int):
        logger.info(f"Betitem {bet_item_id} wurde abgefragt.")
        return self.get_or_404(bet_item_id)

    @router.post("/create", response_model=BetitemResponse)
    def create_betitem(self, betitem: BetitemCreate):
        """
        Achtung:
        Normalerweise sollte Betitem automatisch durch /bet/create erstellt werden.
        Dieser Endpoint ist eher für Tests oder Admin/Debug gedacht.
        """

        self.check_bet_exists(betitem.bet_id)
        self.check_match_exists(betitem.match_id)

        db_betitem = models.DBBetitem(
            bet_id=betitem.bet_id,
            match_id=betitem.match_id,
            bet_money=betitem.bet_money,
            status=betitem.status,
            bet_type=betitem.bet_type,
            prediction=betitem.prediction,
            odds=betitem.odds
        )

        self.db.add(db_betitem)
        self.db.commit()
        self.db.refresh(db_betitem)

        logger.info(
            f"Betitem erstellt: bet_item_id={db_betitem.bet_item_id}, "
            f"bet_id={db_betitem.bet_id}, match_id={db_betitem.match_id}, "
            f"prediction={db_betitem.prediction}, bet_money={db_betitem.bet_money}, "
            f"odds={db_betitem.odds}, status={db_betitem.status}"
        )

        return db_betitem

    @router.put("/{bet_item_id}", response_model=BetitemResponse)
    def update_betitem(self, bet_item_id: int, betitem: BetitemCreate):
        db_betitem = self.get_or_404(bet_item_id)

        self.check_bet_exists(betitem.bet_id)
        self.check_match_exists(betitem.match_id)

        db_betitem.bet_id = betitem.bet_id
        db_betitem.match_id = betitem.match_id
        db_betitem.bet_money = betitem.bet_money
        db_betitem.status = betitem.status
        db_betitem.bet_type = betitem.bet_type
        db_betitem.prediction = betitem.prediction
        db_betitem.odds = betitem.odds

        self.db.commit()
        self.db.refresh(db_betitem)

        logger.info(
            f"Betitem aktualisiert: bet_item_id={db_betitem.bet_item_id}, "
            f"bet_id={db_betitem.bet_id}, match_id={db_betitem.match_id}, "
            f"prediction={db_betitem.prediction}, status={db_betitem.status}"
        )

        return db_betitem

    @router.delete("/{bet_item_id}")
    def delete_betitem(self, bet_item_id: int):
        db_betitem = self.get_or_404(bet_item_id)

        self.db.delete(db_betitem)
        self.db.commit()

        logger.info(f"Betitem gelöscht: bet_item_id={bet_item_id}")

        return {"message": "Betitem gelöscht"}
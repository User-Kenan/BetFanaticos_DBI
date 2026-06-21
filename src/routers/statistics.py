import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy import func, case
from sqlalchemy.orm import Session

import BetFanaticos_DBI.src.models as models
from BetFanaticos_DBI.src.database import get_db


logger = logging.getLogger("betfanaticos.statistics")

router = APIRouter(prefix="/statistics", tags=["Statistics"])


class MatchResultCreate(BaseModel):
    match_id: int
    score_home: int
    score_away: int

    @field_validator("match_id")
    @classmethod
    def match_id_must_be_positive(cls, value: int):
        if value <= 0:
            raise ValueError("match_id muss größer als 0 sein")
        return value

    @field_validator("score_home", "score_away")
    @classmethod
    def score_must_not_be_negative(cls, value: int):
        if value < 0:
            raise ValueError("Scores dürfen nicht negativ sein")
        return value


def normalize_prediction(value: str | None):
    """
    Prediction wird auf feste Werte normalisiert:
    home, away oder draw.
    Es werden keine Teamnamen mehr verglichen.
    """
    if value is None:
        return None

    value = value.lower().strip()

    if value in ["home", "heim", "heimsieg", "1"]:
        return "home"

    if value in ["away", "auswaerts", "auswärts", "auswaertssieg", "auswärtssieg", "2"]:
        return "away"

    if value in ["draw", "x", "unentschieden", "remis"]:
        return "draw"

    return value


def get_match_result(score_home: int, score_away: int):
    if score_home > score_away:
        return "home"

    if score_away > score_home:
        return "away"

    return "draw"


def get_or_create_statistics(db: Session, user_id: int):
    statistics = (
        db.query(models.DBStatistics)
        .filter(models.DBStatistics.user_id == user_id)
        .first()
    )

    if statistics is None:
        statistics = models.DBStatistics(user_id=user_id)
        db.add(statistics)
        db.flush()

        logger.info("Neue Statistics-Zeile für user_id=%s erstellt", user_id)

    return statistics


def recalculate_statistics_for_user(db: Session, user_id: int):
    """
    Aggregiert alle Wetten eines Users und speichert sie in statistics.
    """

    user = (
        db.query(models.DBUser)
        .filter(models.DBUser.userId == user_id)
        .first()
    )

    if user is None:
        raise HTTPException(status_code=404, detail="User nicht gefunden")

    bet_count = (
        db.query(func.count(models.DBBet.bet_id))
        .filter(models.DBBet.user_id == user_id)
        .scalar()
    ) or 0

    status_lower = func.lower(models.DBBetitem.status)

    result = (
        db.query(
            func.coalesce(
                func.sum(
                    case(
                        (status_lower.in_(["won", "gewonnen", "richtig"]), 1),
                        else_=0
                    )
                ),
                0
            ).label("bet_won"),

            func.coalesce(
                func.sum(
                    case(
                        (status_lower.in_(["lost", "verloren", "falsch"]), 1),
                        else_=0
                    )
                ),
                0
            ).label("bet_lost"),

            func.coalesce(
                func.sum(
                    case(
                        (
                            status_lower.in_(["won", "gewonnen", "richtig"]),
                            models.DBBetitem.bet_money * (models.DBBetitem.odds - 1)
                        ),
                        (
                            status_lower.in_(["lost", "verloren", "falsch"]),
                            -models.DBBetitem.bet_money
                        ),
                        else_=0
                    )
                ),
                0
            ).label("profit"),

            func.coalesce(
                func.max(
                    case(
                        (
                            status_lower.in_(["won", "gewonnen", "richtig"]),
                            models.DBBetitem.bet_money * (models.DBBetitem.odds - 1)
                        ),
                        else_=0
                    )
                ),
                0
            ).label("biggest_win"),

            func.coalesce(
                func.min(
                    case(
                        (
                            status_lower.in_(["lost", "verloren", "falsch"]),
                            -models.DBBetitem.bet_money
                        ),
                        else_=0
                    )
                ),
                0
            ).label("biggest_lost")
        )
        .join(models.DBBet, models.DBBet.bet_id == models.DBBetitem.bet_id)
        .filter(models.DBBet.user_id == user_id)
        .first()
    )

    bet_won = result.bet_won or 0
    bet_lost = result.bet_lost or 0
    finished_bets = bet_won + bet_lost

    if finished_bets > 0:
        win_rate = round((bet_won / finished_bets) * 100, 2)
    else:
        win_rate = 0

    statistics = get_or_create_statistics(db, user_id)

    statistics.bet_count = bet_count
    statistics.bet_won = bet_won
    statistics.bet_lost = bet_lost
    statistics.win_rate = win_rate
    statistics.profit = round(float(result.profit or 0), 2)
    statistics.biggest_win = round(float(result.biggest_win or 0), 2)
    statistics.biggest_lost = round(float(result.biggest_lost or 0), 2)

    logger.info(
        "Statistik aggregiert: user_id=%s, bet_count=%s, won=%s, lost=%s, win_rate=%s%%",
        user_id,
        bet_count,
        bet_won,
        bet_lost,
        win_rate
    )

    return statistics


@router.post("/results")
def post_match_result(result: MatchResultCreate, db: Session = Depends(get_db)):
    """
    Dummy-Ergebnis für ein Match posten.
    Danach werden alle Betitems zu diesem Match ausgewertet
    und die statistics-Tabelle aktualisiert.
    """

    match = (
        db.query(models.DBMatch)
        .filter(models.DBMatch.match_id == result.match_id)
        .first()
    )

    if match is None:
        logger.warning(
            "Result konnte nicht gespeichert werden: match_id=%s nicht gefunden",
            result.match_id
        )
        raise HTTPException(status_code=404, detail="Match nicht gefunden")

    match.score_home = result.score_home
    match.score_away = result.score_away

    actual_result = get_match_result(result.score_home, result.score_away)

    bet_items = (
        db.query(models.DBBetitem)
        .filter(models.DBBetitem.match_id == result.match_id)
        .all()
    )

    affected_user_ids = set()
    affected_bet_ids = set()

    won_count = 0
    lost_count = 0

    logger.info(
        "Match-Result gepostet: match_id=%s, score=%s:%s, result=%s, betitems=%s",
        result.match_id,
        result.score_home,
        result.score_away,
        actual_result,
        len(bet_items)
    )

    for bet_item in bet_items:
        prediction = normalize_prediction(bet_item.prediction)

        if prediction == actual_result:
            bet_item.status = "won"
            won_count += 1
        else:
            bet_item.status = "lost"
            lost_count += 1

        bet = (
            db.query(models.DBBet)
            .filter(models.DBBet.bet_id == bet_item.bet_id)
            .first()
        )

        if bet:
            bet.status = "finished"
            affected_user_ids.add(bet.user_id)
            affected_bet_ids.add(bet.bet_id)

        logger.info(
            "Betitem ausgewertet: bet_item_id=%s, bet_id=%s, prediction=%s, result=%s, status=%s",
            bet_item.bet_item_id,
            bet_item.bet_id,
            prediction,
            actual_result,
            bet_item.status
        )

    for user_id in affected_user_ids:
        recalculate_statistics_for_user(db, user_id)

    db.commit()

    logger.info(
        "Result fertig verarbeitet: match_id=%s, won=%s, lost=%s, affected_users=%s",
        result.match_id,
        won_count,
        lost_count,
        list(affected_user_ids)
    )

    return {
        "message": "Result gespeichert und Wetten ausgewertet",
        "match_id": result.match_id,
        "score_home": result.score_home,
        "score_away": result.score_away,
        "result": actual_result,
        "won_bets": won_count,
        "lost_bets": lost_count,
        "finished_bets": list(affected_bet_ids),
        "updated_users": list(affected_user_ids)
    }


@router.post("/users/{user_id}/recalculate")
def recalculate_user_statistics(user_id: int, db: Session = Depends(get_db)):
    statistics = recalculate_statistics_for_user(db, user_id)

    db.commit()
    db.refresh(statistics)

    return {
        "message": "Statistik neu berechnet",
        "user_id": statistics.user_id,
        "bet_count": statistics.bet_count,
        "bet_won": statistics.bet_won,
        "bet_lost": statistics.bet_lost,
        "win_rate": statistics.win_rate,
        "profit": statistics.profit,
        "biggest_win": statistics.biggest_win,
        "biggest_lost": statistics.biggest_lost
    }


@router.get("/users/{user_id}")
def get_user_statistics(user_id: int, db: Session = Depends(get_db)):
    """
    Holt die gespeicherte Statistik aus der statistics-Tabelle.
    Hier wird zusätzlich mit users gejoint, damit der Username mitkommt.
    """

    result = (
        db.query(models.DBStatistics, models.DBUser)
        .join(models.DBUser, models.DBUser.userId == models.DBStatistics.user_id)
        .filter(models.DBStatistics.user_id == user_id)
        .first()
    )

    if result is None:
        raise HTTPException(status_code=404, detail="Statistik nicht gefunden")

    statistics, user = result

    logger.info("Statistik geladen: user_id=%s, name=%s", user.userId, user.name)

    return {
        "user_id": user.userId,
        "name": user.name,
        "bet_count": statistics.bet_count,
        "bet_won": statistics.bet_won,
        "bet_lost": statistics.bet_lost,
        "win_rate": statistics.win_rate,
        "profit": statistics.profit,
        "biggest_win": statistics.biggest_win,
        "biggest_lost": statistics.biggest_lost
    }
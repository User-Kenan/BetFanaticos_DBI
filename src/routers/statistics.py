from sqlalchemy import select, func, case

from BetFanaticos_DBI.src import models
from fastapi import APIRouter, Depends, HTTPException
from fastapi_restful.cbv import cbv
from pydantic import BaseModel
from sqlalchemy.orm import Session
from BetFanaticos_DBI.src.database import get_db
from BetFanaticos_DBI.src.models import DBBetitem,DBUser,DBBet

router = APIRouter(prefix="/statistics", tags=["Statistics"])


class StatisticsCreate(BaseModel):
    user_id: int
    win_rate: float
    biggest_win: float
    biggest_lost: float
    bet_lost: int
    bet_won: int
    profit: float


class StatisticsResponse(StatisticsCreate):
    statisticsID: int

    class Config:
        from_attributes = True


@cbv(router)
class StatisticsAPI:

    db: Session = Depends(get_db)

    def get_or_404(self, statistics_id: int):
        statistics = self.db.query(models.DBStatistics).filter(
            models.DBStatistics.statisticsID == statistics_id
        ).first()

        if statistics is None:
            raise HTTPException(status_code=404, detail="Statistik nicht gefunden")

        return statistics

    from fastapi import APIRouter, Depends, HTTPException
    from sqlalchemy import select, func, case
    from sqlalchemy.ext.asyncio import AsyncSession



    router = APIRouter(prefix="/statistics", tags=["Statistics"])

    @router.get("/{user_id}")
    async def get_statistics(
            user_id: int,
            db: AsyncSession = Depends(get_db)
    ):
    #KI
    #Chatgpt
    # Prompt
        stmt = (
            select(
                DBUser.user_id,

                func.count(func.distinct(DBBet.bet_id)).label("total_bets"),

                func.sum(
                    case(
                        (DBBet.status == "won", 1),
                        else_=0
                    )
                ).label("bet_won"),

                func.sum(
                    case(
                        (DBBet.status == "lost", 1),
                        else_=0
                    )
                ).label("bet_lost"),

                func.sum(
                    case(
                        (
                            DBBet.status == "won",
                            DBBetitem.payout - DBBetitem.bet_money
                        ),
                        else_=-DBBetitem.bet_money
                    )
                ).label("profit"),

                func.max(
                    case(
                        (
                            DBBet.status == "won",
                            DBBetitem.payout - DBBetitem.bet_money
                        ),
                        else_=None
                    )
                ).label("biggest_win"),

                func.min(
                    case(
                        (
                            DBBet.status == "lost",
                            -DBBetitem.bet_money
                        ),
                        else_=None
                    )
                ).label("biggest_lost")
            )
            .join(DBBet, DBUser.user_id == DBBet.user_id)
            .join(DBBetitem, DBBetitem.bet_id == DBBetitem.bet_id)
            .where(DBUser.user_id == user_id)
            .group_by(DBUser.user_id)
        )

        result = await db.execute(stmt)
        stats = result.first()

        if not stats:
            raise HTTPException(
                status_code=404,
                detail="No statistics found"
            )

        total_bets = stats.total_bets or 0
        bet_won = stats.bet_won or 0

        win_rate = (
            round((bet_won / total_bets) * 100, 2)
            if total_bets > 0
            else 0
        )

        return {
            "userId": stats.user_id,
            "winRate": win_rate,
            "biggestWin": stats.biggest_win or 0,
            "biggestLost": stats.biggest_lost or 0,
            "betWon": stats.bet_won or 0,
            "betLost": stats.bet_lost or 0,
            "profit": stats.profit or 0
        }

    @router.get("/", response_model=list[StatisticsResponse])
    def get_all_statistics(self):
        return self.db.query(models.DBStatistics).all()

    @router.get("/{statistics_id}", response_model=StatisticsResponse)
    def get_statistics(self, statistics_id: int):
        return self.get_or_404(statistics_id)


    @router.post("/", response_model=StatisticsResponse)
    def create_statistics(self, statistics: StatisticsCreate):
        db_statistics = models.DBStatistics(
            user_id=statistics.user_id,
            win_rate=statistics.win_rate,
            biggest_win=statistics.biggest_win,
            biggest_lost=statistics.biggest_lost,
            bet_lost=statistics.bet_lost,
            bet_won=statistics.bet_won,
            profit=statistics.profit
        )

        self.db.add(db_statistics)
        self.db.commit()
        self.db.refresh(db_statistics)

        return db_statistics

    @router.put("/{statistics_id}", response_model=StatisticsResponse)
    def update_statistics(self, statistics_id: int, statistics: StatisticsCreate):
        db_statistics = self.get_or_404(statistics_id)

        db_statistics.user_id = statistics.user_id
        db_statistics.win_rate = statistics.win_rate
        db_statistics.biggest_win = statistics.biggest_win
        db_statistics.biggest_lost = statistics.biggest_lost
        db_statistics.bet_lost = statistics.bet_lost
        db_statistics.bet_won = statistics.bet_won
        db_statistics.profit = statistics.profit

        self.db.commit()
        self.db.refresh(db_statistics)

        return db_statistics

    @router.delete("/{statistics_id}")
    def delete_statistics(self, statistics_id: int):
        db_statistics = self.get_or_404(statistics_id)

        self.db.delete(db_statistics)
        self.db.commit()

        return {"message": "Statistik gelöscht"}
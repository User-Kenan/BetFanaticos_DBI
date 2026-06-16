from BetFanaticos_DBI.temp import models
from BetFanaticos_DBI.temp.database import get_db
from fastapi import APIRouter, Depends, HTTPException
from fastapi_restful.cbv import cbv
from pydantic import BaseModel
from sqlalchemy.orm import Session

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
from fastapi import APIRouter, Depends, HTTPException
from fastapi_restful.cbv import cbv
from pydantic import BaseModel
from sqlalchemy.orm import Session
import requests

from BetFanaticos_DBI.src import models
from BetFanaticos_DBI.src.database import get_db

router = APIRouter(prefix="/match", tags=["Match"])

API_KEY_Football = "cc9941e4e76441ad860b0b38da3fb426"


class MatchCreate(BaseModel):
    away_team: str
    home_away: str
    score_home: int
    score_away: int
    time: str
    league: str


class MatchResponse(MatchCreate):
    match_id: int

    class Config:
        from_attributes = True


@cbv(router)
class MatchAPI:

    db: Session = Depends(get_db)

    def get_or_404(self, match_id: int):
        match = self.db.query(models.DBMatch).filter(
            models.DBMatch.match_id == match_id
        ).first()

        if match is None:
            raise HTTPException(status_code=404, detail="Match nicht gefunden")

        return match

    @router.get("/football-api")
    def get_football_api_matches(self):
        headers = {
            "X-Auth-Token": API_KEY_Football
        }

        response = requests.get(
            "https://api.football-data.org/v4/competitions/PL/matches",
            headers=headers
        )

        data = response.json()

        matches = []

        for match in data["matches"]:
            matches.append({
                "homeTeam": match["homeTeam"]["name"],
                "awayTeam": match["awayTeam"]["name"],
                "league": "Premier League",
                "sportType": "Football",
                "matchDate": match["utcDate"],
                "homeScore": match["score"]["fullTime"]["home"] or 0,
                "awayScore": match["score"]["fullTime"]["away"] or 0
            })

        return matches[:30]

    @router.get("/basketball-api")
    def get_basketball_api_matches(self):
        response = requests.get(
            "https://www.thesportsdb.com/api/v1/json/123/eventsseason.php?id=4387&s=2026-2027"
        )

        data = response.json()
        matches = []

        if data["events"] is None:
            return matches

        for match in data["events"]:
            matches.append({
                "homeTeam": match["strHomeTeam"],
                "awayTeam": match["strAwayTeam"],
                "league": "NBA",
                "sportType": "Basketball",
                "matchDate": match["dateEvent"] + "T" + (match["strTime"] or "00:00:00"),
                "homeScore": int(match["intHomeScore"] or 0),
                "awayScore": int(match["intAwayScore"] or 0)
            })

        return matches[:30]

    @router.get("/", response_model=list[MatchResponse])
    def get_all_matches(self):
        return self.db.query(models.DBMatch).all()

    @router.get("/{match_id}", response_model=MatchResponse)
    def get_match(self, match_id: int):
        return self.get_or_404(match_id)

    @router.post("/", response_model=MatchResponse)
    def create_match(self, match: MatchCreate):
        db_match = models.DBMatch(
            away_team=match.away_team,
            home_away=match.home_away,
            score_home=match.score_home,
            score_away=match.score_away,
            time=match.time,
            league=match.league
        )

        self.db.add(db_match)
        self.db.commit()
        self.db.refresh(db_match)

        return db_match

    @router.put("/{match_id}", response_model=MatchResponse)
    def update_match(self, match_id: int, match: MatchCreate):
        db_match = self.get_or_404(match_id)

        db_match.away_team = match.away_team
        db_match.home_away = match.home_away
        db_match.score_home = match.score_home
        db_match.score_away = match.score_away
        db_match.time = match.time
        db_match.league = match.league

        self.db.commit()
        self.db.refresh(db_match)

        return db_match

    @router.delete("/{match_id}")
    def delete_match(self, match_id: int):
        db_match = self.get_or_404(match_id)

        self.db.delete(db_match)
        self.db.commit()

        return {"message": "Match gelöscht"}
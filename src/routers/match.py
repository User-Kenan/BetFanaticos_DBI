from fastapi import APIRouter, Depends, HTTPException
from fastapi_restful.cbv import cbv
from pydantic import BaseModel
from sqlalchemy.orm import Session
import requests
from datetime import datetime

import models
from database import get_db

router = APIRouter(prefix="/match", tags=["Match"])

# API Key von der Fussball API
API_KEY = "cc9941e4e76441ad860b0b38da3fb426"


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

    # status des Matches
    def convert_status(self, api_status):
        if api_status == "FINISHED":
            return "Finished"
        if api_status in ["LIVE", "IN_PLAY", "PAUSED"]:
            return "Live"
        return "Upcoming"

    # KI hier
    def calculate_strength(self, team_data):
        points = team_data.get("points", 0)
        won = team_data.get("won", 0)
        goal_difference = team_data.get("goalDifference", 0)

        strength = points + won * 3 + goal_difference

        if strength <= 0:
            strength = 1

        return strength

    def calculate_odds(self, home_strength, away_strength):
        total = home_strength + away_strength

        home_probability = home_strength / total
        away_probability = away_strength / total

        home_odds = round(1 / home_probability, 2)
        away_odds = round(1 / away_probability, 2)

        if home_odds < 1.1:
            home_odds = 1.1

        if away_odds < 1.1:
            away_odds = 1.1

        draw_odds = 3.2

        return home_odds, draw_odds, away_odds

    # bis hier => Rechnet die Teamstärke sowie die Quote


    # Holt sich die Team Stärke
    def get_team_strengths(self, competition_code, headers):
        strengths = {}

        try:
            response = requests.get(
                f"https://api.football-data.org/v4/competitions/{competition_code}/standings",
                headers=headers,
                timeout=10
            )

            data = response.json()

            if "standings" not in data:
                return strengths

            for standing in data["standings"]:
                for team in standing.get("table", []):
                    team_name = team["team"]["name"]
                    strengths[team_name] = self.calculate_strength(team)

        except requests.exceptions.RequestException:
            return strengths

        return strengths

    def get_or_404(self, match_id: int):
        match = self.db.query(models.DBMatch).filter(
            models.DBMatch.match_id == match_id
        ).first()

        if match is None:
            raise HTTPException(status_code=404, detail="Match nicht gefunden")

        return match


    # Ruft zukünftige Fussballspiele ab und berechnet passenden Wettquote
    @router.get("/football-api")
    def get_football_api_matches(self):
        headers = {
            "X-Auth-Token": API_KEY
        }

        competition_code = "WC" # WM spiele werden angeziegt

        # Versucht die Spiele auszurufen
        try:
            response = requests.get(
                f"https://api.football-data.org/v4/competitions/{competition_code}/matches",
                headers=headers,
                timeout=10
            )
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=503,
                detail=f"Football API nicht erreichbar: {str(e)}"
            )

        data = response.json()

        if "matches" not in data:
            raise HTTPException(
                status_code=response.status_code,
                detail=data
            )

        team_strengths = self.get_team_strengths(competition_code, headers)

        now = datetime.utcnow()
        matches = []

        for match in data["matches"]:
            match_date = datetime.fromisoformat(
                match["utcDate"].replace("Z", "+00:00")
            ).replace(tzinfo=None)

            if match_date < now:
                continue

            home_team = match["homeTeam"]["name"]
            away_team = match["awayTeam"]["name"]

            home_strength = team_strengths.get(home_team, 50)
            away_strength = team_strengths.get(away_team, 50)

            home_odds, draw_odds, away_odds = self.calculate_odds(
                home_strength,
                away_strength
            )

            matches.append({
                "id": match["id"],
                "homeTeam": home_team,
                "awayTeam": away_team,
                "league": "World Cup",
                "sportType": "Football",
                "matchDate": match["utcDate"],
                "homeScore": match["score"]["fullTime"]["home"] or 0,
                "awayScore": match["score"]["fullTime"]["away"] or 0,
                "homeOdds": home_odds,
                "drawOdds": draw_odds,
                "awayOdds": away_odds,
                "status": self.convert_status(match["status"])
            })

        return matches[:30]

    # Ruft kommende Basketballspiele
    @router.get("/basketball-api")
    def get_basketball_api_matches(self):
        response = requests.get(
            "https://www.thesportsdb.com/api/v1/json/123/eventsnextleague.php?id=4516"
        )

        data = response.json()
        matches = []

        if data["events"] is None:
            return matches

        for match in data["events"]:
            matches.append({
                "id": int(match["idEvent"]),
                "homeTeam": match["strHomeTeam"],
                "awayTeam": match["strAwayTeam"],
                "league": "NBA",
                "sportType": "Basketball",
                "matchDate": match["dateEvent"] + "T" + (match["strTime"] or "00:00:00"),
                "homeScore": int(match["intHomeScore"] or 0),
                "awayScore": int(match["intAwayScore"] or 0),
                "homeOdds": 1.9,
                "drawOdds": 3.2,
                "awayOdds": 1.9,
                "status": "Upcoming"
            })

        return matches[:30]


    # Gibt alle gespeicherten Spiele aus der DB zurück
    @router.get("/", response_model=list[MatchResponse])
    def get_all_matches(self):
        return self.db.query(models.DBMatch).all()

    # Gibt spiele anhand der id zurück
    @router.get("/{match_id}", response_model=MatchResponse)
    def get_match(self, match_id: int):
        return self.get_or_404(match_id)

    # Erstellt neues Spiel und speichert sie in die DB
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

    # Aktualisiert die Daten eines vorhandenen Spiels.
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

    # Löscht ein Spiel aus der DB
    @router.delete("/{match_id}")
    def delete_match(self, match_id: int):
        db_match = self.get_or_404(match_id)

        self.db.delete(db_match)
        self.db.commit()

        return {"message": "Match gelöscht"}
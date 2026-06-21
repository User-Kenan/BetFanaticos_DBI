from database import Base
from sqlalchemy import Column, Integer, String, Double, ForeignKey, Boolean, DateTime
from datetime import datetime


class DBUser(Base):
    __tablename__ = "users"

    userId = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True,unique=True)
    password = Column(String, nullable=False)
    role = Column(String, default="user")
    api_key = Column(String, unique=True, nullable=True)


class DBStatistics(Base):
    __tablename__ = "statistics"

    statisticsID = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.userId"))
    win_rate = Column(Double)
    biggest_win = Column(Double)
    biggest_lost = Column(Double)
    bet_lost = Column(Integer, index=True)
    bet_won = Column(Integer, index=True)
    profit = Column(Double)


class DBWallet(Base):
    __tablename__ = "wallet"

    wallet_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.userId"))
    coins = Column(Double)

class DBUserChallenge(Base):
    __tablename__ = "user_challenges"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.userId"))
    challenge_id = Column(Integer, ForeignKey("sidequests.id"))

    current_state = Column(Integer, default=0)
    completed = Column(Boolean, default=False)
    reward_claimed = Column(Boolean, default=False)

class DBBet(Base):
    __tablename__ = "bets"

    bet_id = Column(Integer, primary_key=True, index=True)
    status = Column(String(20))
    user_id = Column(Integer, ForeignKey("users.userId"))


class DBBetitem(Base):
    __tablename__ = "betitem"

    bet_item_id = Column(Integer, primary_key=True, index=True)

    bet_money = Column(Double)
    status = Column(String)
    bet_type = Column(String)

    prediction = Column(String)
    odds = Column(Double)

    home_team = Column(String)
    away_team = Column(String)

    score_team_a = Column(Integer, index=True)
    score_team_b = Column(Integer, index=True)

    bet_id = Column(Integer, ForeignKey("bets.bet_id"))
    match_id = Column(Integer)


class DBMatch(Base):
    __tablename__ = "matches"

    match_id = Column(Integer, primary_key=True, index=True)
    away_team = Column(String, index=True)
    home_away = Column(String, index=True)
    score_home = Column(Integer)
    score_away = Column(Integer)
    time = Column(String)
    league = Column(String)


class DBJunctionTable(Base):
    __tablename__ = "junctiontableside"

    side_quest_id = Column(
        Integer,
        ForeignKey("sidequests.id"),
        primary_key=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.userId"),
        primary_key=True
    )


class DBChallenge(Base):
    __tablename__ = "sidequests"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, index=True)
    description = Column(String)

    required_amount = Column(Integer)
    reward = Column(Integer)







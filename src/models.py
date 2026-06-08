from sqlalchemy import Column, Integer, String, Double, ForeignKey
from src.database import Base


class DBUser(Base):
    __tablename__ = "users"

    userId = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), nullable=False, index=True)
    password = Column(String(8), nullable=False)


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


class DBBet(Base):
    __tablename__ = "bets"

    bet_id = Column(Integer, primary_key=True, index=True)
    status = Column(String(20))
    user_id = Column(Integer, ForeignKey("users.userId"))


class DBBetitem(Base):
    __tablename__ = "betitem"

    bet_item_id = Column(Integer, primary_key=True, index=True)
    score_team_a = Column(Integer, index=True)
    score_team_b = Column(Integer, index=True)
    bet_money = Column(Double)
    status = Column(String)
    bet_type = Column(String)

    bet_id = Column(Integer, ForeignKey("bets.bet_id"))
    match_id = Column(Integer, ForeignKey("matches.match_id"))


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
        ForeignKey("sidequests.side_quest_id"),
        primary_key=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.userId"),
        primary_key=True
    )


class DBSidequest(Base):
    __tablename__ = "sidequests"

    side_quest_id = Column(Integer, primary_key=True, index=True)
    challange = Column(String, index=True)
    start_date = Column(String, index=True)
    end_date = Column(String, index=True)
    earned_coins = Column(Integer)
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Double
from BetFanaticos_DBI.database import Base


class DBUser(Base):
    __tablename__ = "users"

    userId = Column(Integer, primary_key=True, index=True)
    name = Column(String(20),nullable=False)
    password = Column(String(8),index=True)


class DBStatistics(Base):
    __tablename__ = "statistics"

    statisticsID = Column(Integer,primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    win_rate = Column(Double)
    biggest_win = Column(Double)
    biggest_lost = Column(Double)
    bet_lost = Column(Integer)
    bet_won = Column(Integer)
    profit = Column(Double)


class DBWallet(Base):
    __tablename__ = "wallet"

    wallet_id = Column(Integer,primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    coins = Column(Double)

class DBBet(Base):
    __tablename__ = "bets"

    bet_id = Column(Integer,primary_key=True)
    status = Column(String(20))
    user_id = Column(Integer, ForeignKey("users.id"))

class DBBetitem(Base):
    __tablename__ = "betitem"

    bet_item_id = Column(Integer,primary_key=True)
    score_team_a = Column(Integer)
    score_team_a = Column(Integer)




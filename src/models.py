from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Double,
    ForeignKey,
    Boolean,
    DateTime,
    UniqueConstraint,
)

from BetFanaticos_DBI.src.database import Base


class DBUser(Base):
    __tablename__ = "users"

    userId = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False, unique=True, index=True)
    password = Column(String, nullable=False)

    role = Column(String, default="user", nullable=False)

    api_key = Column(String, unique=True, nullable=True)


class DBStatistics(Base):
    __tablename__ = "statistics"

    statisticsID = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.userId"), nullable=False, unique=True)

    # Wie oft der User insgesamt gewettet hat
    bet_count = Column(Integer, default=0, nullable=False)

    # Wie oft richtig/falsch
    bet_won = Column(Integer, default=0, nullable=False, index=True)
    bet_lost = Column(Integer, default=0, nullable=False, index=True)

    # Gewinnrate in Prozent
    win_rate = Column(Double, default=0, nullable=False)

    # Profit-Berechnung
    profit = Column(Double, default=0, nullable=False)
    biggest_win = Column(Double, default=0, nullable=False)
    biggest_lost = Column(Double, default=0, nullable=False)


class DBWallet(Base):
    __tablename__ = "wallet"

    wallet_id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.userId"), nullable=False, unique=True)

    coins = Column(Double, default=0, nullable=False)


class DBBet(Base):
    __tablename__ = "bets"

    bet_id = Column(Integer, primary_key=True, index=True)

    # z. B. open, won, lost, cancelled
    status = Column(String(20), default="open", nullable=False)

    user_id = Column(Integer, ForeignKey("users.userId"), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class DBBetitem(Base):
    __tablename__ = "betitem"

    bet_item_id = Column(Integer, primary_key=True, index=True)

    bet_id = Column(Integer, ForeignKey("bets.bet_id"), nullable=False)


    match_id = Column(Integer, ForeignKey("matches.match_id"), nullable=False)

    bet_money = Column(Double, nullable=False)
    status = Column(String(20), default="open", nullable=False)
    bet_type = Column(String, default="winner", nullable=False)
    prediction = Column(String(20), nullable=False)
    odds = Column(Double, nullable=False)


class DBMatch(Base):
    __tablename__ = "matches"

    match_id = Column(Integer, primary_key=True, index=True)

    home_team = Column(String, nullable=False, index=True)
    away_team = Column(String, nullable=False, index=True)

    score_home = Column(Integer, nullable=True)
    score_away = Column(Integer, nullable=True)

    time = Column(String, nullable=True)
    league = Column(String, nullable=True, index=True)


class DBChallenge(Base):
    __tablename__ = "sidequests"

    id = Column(Integer, primary_key=True, index=True)

    type = Column(String, index=True, nullable=False)
    description = Column(String, nullable=False)

    required_amount = Column(Integer, nullable=False)
    reward = Column(Integer, nullable=False)


class DBUserChallenge(Base):
    __tablename__ = "user_challenges"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.userId"), nullable=False)
    challenge_id = Column(Integer, ForeignKey("sidequests.id"), nullable=False)

    current_state = Column(Integer, default=0, nullable=False)

    completed = Column(Boolean, default=False, nullable=False)
    reward_claimed = Column(Boolean, default=False, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "challenge_id", name="unique_user_challenge"),
    )


class DBJunctionTable(Base):
    """
    Junction table wird nicht mehr gebraucht, anfang idee war es, sidequest mit user zu connecten
    """

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
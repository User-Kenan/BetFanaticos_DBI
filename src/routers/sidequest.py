from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from BetFanaticos_DBI.src.database import get_db
from BetFanaticos_DBI.src import models

router = APIRouter(prefix="/challenges", tags=["Challenges"])


@router.post("/seed")
def seed_challenges(db: Session = Depends(get_db)):
    challenges = [
        models.DBChallenge(
            id=1,
            type="DailyLogin",
            description="Logge dich einmal ein",
            required_amount=1,
            reward=25
        ),
        models.DBChallenge(
            id=2,
            type="PlacePrediction",
            description="Gib 3 Predictions ab",
            required_amount=3,
            reward=100
        ),
        models.DBChallenge(
            id=3,
            type="CorrectPrediction",
            description="Treffe 1 richtige Prediction",
            required_amount=1,
            reward=50
        )
    ]

    for c in challenges:
        if not db.query(models.DBChallenge).filter(models.DBChallenge.id == c.id).first():
            db.add(c)

    db.commit()

    return {"message": "Challenges erstellt"}


@router.get("/all")
def get_all_challenges(db: Session = Depends(get_db)):
    return db.query(models.DBChallenge).all()


@router.get("/user/{user_id}")
def get_user_challenges(user_id: int, db: Session = Depends(get_db)):
    challenges = db.query(models.DBChallenge).all()

    result = []

    for challenge in challenges:
        user_challenge = db.query(models.DBUserChallenge).filter(
            models.DBUserChallenge.user_id == user_id,
            models.DBUserChallenge.challenge_id == challenge.id
        ).first()

        if user_challenge is None:
            user_challenge = models.DBUserChallenge(
                user_id=user_id,
                challenge_id=challenge.id,
                current_state=0,
                completed=False,
                reward_claimed=False
            )
            db.add(user_challenge)
            db.flush()

        result.append({
            "id": challenge.id,
            "type": challenge.type,
            "description": challenge.description,
            "required_amount": challenge.required_amount,
            "reward": challenge.reward,
            "current_state": user_challenge.current_state,
            "completed": user_challenge.completed,
            "reward_claimed": user_challenge.reward_claimed
        })

    db.commit()

    return result


@router.post("/update")
def update_challenge(
    user_id: int,
    challenge_id: int,
    amount: int,
    db: Session = Depends(get_db)
):
    challenge = db.query(models.DBChallenge).filter(
        models.DBChallenge.id == challenge_id
    ).first()

    if challenge is None:
        raise HTTPException(status_code=404, detail="Challenge nicht gefunden")

    user_challenge = db.query(models.DBUserChallenge).filter(
        models.DBUserChallenge.user_id == user_id,
        models.DBUserChallenge.challenge_id == challenge_id
    ).first()

    if user_challenge is None:
        user_challenge = models.DBUserChallenge(
            user_id=user_id,
            challenge_id=challenge_id,
            current_state=0,
            completed=False,
            reward_claimed=False
        )
        db.add(user_challenge)
        db.flush()

    if not user_challenge.completed:
        user_challenge.current_state += amount

        if user_challenge.current_state >= challenge.required_amount:
            user_challenge.current_state = challenge.required_amount
            user_challenge.completed = True

            if not user_challenge.reward_claimed:
                wallet = db.query(models.DBWallet).filter(
                    models.DBWallet.user_id == user_id
                ).first()

                if wallet is None:
                    wallet = models.DBWallet(
                        user_id=user_id,
                        coins=1000
                    )
                    db.add(wallet)
                    db.flush()

                wallet.coins += challenge.reward
                user_challenge.reward_claimed = True

    db.commit()
    db.refresh(user_challenge)

    return {
        "id": challenge.id,
        "type": challenge.type,
        "description": challenge.description,
        "required_amount": challenge.required_amount,
        "reward": challenge.reward,
        "current_state": user_challenge.current_state,
        "completed": user_challenge.completed,
        "reward_claimed": user_challenge.reward_claimed
    }
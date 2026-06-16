from BetFanaticos_DBI.src import models
from BetFanaticos_DBI.src.database import get_db
from fastapi import APIRouter, Depends, HTTPException
from fastapi_restful.cbv import cbv
from pydantic import BaseModel
from sqlalchemy.orm import Session

router = APIRouter(prefix="/junction", tags=["Junction"])


class JunctionCreate(BaseModel):
    side_quest_id: int
    user_id: int


class JunctionResponse(JunctionCreate):

    class Config:
        from_attributes = True


@cbv(router)
class JunctionAPI:

    db: Session = Depends(get_db)

    @router.get("/", response_model=list[JunctionResponse])
    def get_all(self):
        return self.db.query(models.DBJunctionTable).all()

    @router.post("/", response_model=JunctionResponse)
    def create(self, junction: JunctionCreate):

        db_junction = models.DBJunctionTable(
            side_quest_id=junction.side_quest_id,
            user_id=junction.user_id
        )

        self.db.add(db_junction)
        self.db.commit()
        self.db.refresh(db_junction)

        return db_junction

    @router.delete("/{side_quest_id}/{user_id}")
    def delete(self, side_quest_id: int, user_id: int):

        junction = self.db.query(models.DBJunctionTable).filter(
            models.DBJunctionTable.side_quest_id == side_quest_id,
            models.DBJunctionTable.user_id == user_id
        ).first()

        if junction is None:
            raise HTTPException(status_code=404, detail="Eintrag nicht gefunden")

        self.db.delete(junction)
        self.db.commit()

        return {"message": "Eintrag gelöscht"}
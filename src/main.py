import uvicorn
from BetFanaticos_DBI.src import models
from BetFanaticos_DBI.src.database import engine
from BetFanaticos_DBI.src.routers.admin import router as admin
from BetFanaticos_DBI.src.routers.auth import router as auth
from BetFanaticos_DBI.src.routers.match import router as match_router
from fastapi import FastAPI

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Tierheim API",
    version="1.0.0"
)




app.include_router(match_router)
app.include_router(admin)
app.include_router(auth)



if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
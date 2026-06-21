import uvicorn


import BetFanaticos_DBI.src.models as models
from BetFanaticos_DBI.src.database import engine
from fastapi import FastAPI

from BetFanaticos_DBI.src.routers.wallet import router as wallet
from BetFanaticos_DBI.src.routers.admin import router as admin
from BetFanaticos_DBI.src.routers.auth  import router as auth
from BetFanaticos_DBI.src.routers.match  import router as match_router
from BetFanaticos_DBI.src.routers.sidequest import router as sidequest
from BetFanaticos_DBI.src.routers.bet import router as bet



models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Betfanaticos_API",
    version="1.0.0"
)




app.include_router(match_router)
app.include_router(admin)
app.include_router(auth)
app.include_router(wallet)
app.include_router(sidequest)
app.include_router(bet)



if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
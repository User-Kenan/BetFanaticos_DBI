import uvicorn

import models
from database import engine
from fastapi import FastAPI
from routers import wallet
from routers import betitem


from routers import sidequest
from routers.admin import router as admin
from routers.auth import router as auth
from routers.match import router as match_router
from routers import bet

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Tierheim API",
    version="1.0.0"
)




app.include_router(match_router)
app.include_router(admin)
app.include_router(auth)
app.include_router(wallet.router)
app.include_router(betitem.router)
app.include_router(bet.router)



if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
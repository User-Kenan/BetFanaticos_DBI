from xml.etree.ElementInclude import include
import uvicorn
from fastapi import FastAPI
from BetFanaticos_DBI.src.routers.match import router as match_router
from BetFanaticos_DBI.src.database import engine
# from Hü import tables
#from BetFanaticos_DBI.src.routers.... import router
from BetFanaticos_DBI.src import models
from BetFanaticos_DBI.src.routers.sidequest import router as sidequest_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Tierheim API",
    version="1.0.0"
)

app.include_router(match_router)
app.include_router(sidequest_router)



if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
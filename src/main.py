import uvicorn
from fastapi import FastAPI

from BetFanaticos_DBI.src.database import engine
# from Hü import tables
#from BetFanaticos_DBI.src.routers.... import router

tables.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Tierheim API",
    version="1.0.0"
)

app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
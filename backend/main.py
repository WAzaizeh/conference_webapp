from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from routers.events import router as events_router
from routers.speakers import router as speakers_router
from routers.limiter import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded


# @asynccontextmanager
# async def lifespan(_: FastAPI):
#     yield


app = FastAPI()  # FastAPI(lifespan=lifespan)


app.include_router(events_router)
app.include_router(speakers_router)

app.state.limiter = limiter

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/")
def read_root():
    return "Server is running."
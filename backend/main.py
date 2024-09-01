from routers.limiter import limiter
from fastapi import FastAPI, APIRouter
from contextlib import asynccontextmanager
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from fastapi.middleware.cors import CORSMiddleware
from routers.events import router as events_router
from routers.speakers import router as speakers_router



# @asynccontextmanager
# async def lifespan(_: FastAPI):
#     yield


app = FastAPI()  # FastAPI(lifespan=lifespan)

# middleware to allow CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(events_router)
app.include_router(speakers_router)

app.state.limiter = limiter

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/")
def read_root():
    return "Server is running."
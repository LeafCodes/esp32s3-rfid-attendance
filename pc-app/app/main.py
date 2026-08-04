from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import attendance, cards, export, dashboard
from app.database import engine, Base
from app.services.mdns import start_mdns, stop_mdns
import asyncio

app = FastAPI(title="RFID Attendance System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(attendance.router)
app.include_router(cards.router)
app.include_router(export.router)
app.include_router(dashboard.router)


@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, start_mdns)


@app.on_event("shutdown")
async def shutdown():
    stop_mdns()

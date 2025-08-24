from fastapi import FastAPI

from .routers import runs, events, files, artifacts, debug

app = FastAPI()

app.include_router(runs.router)
app.include_router(events.router)
app.include_router(files.router)
app.include_router(artifacts.router)
app.include_router(debug.router)


@app.get("/")
async def root() -> dict:
    return {"message": "API Gateway"}

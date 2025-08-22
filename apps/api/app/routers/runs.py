from fastapi import APIRouter

router = APIRouter()

@router.post('/runs/start')
async def start_run():
    return {"status": "started"}

@router.get('/runs/{run_id}')
async def get_run(run_id: str):
    return {"run_id": run_id}

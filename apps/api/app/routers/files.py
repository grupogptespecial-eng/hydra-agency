from fastapi import APIRouter

router = APIRouter()

@router.get('/files/{path:path}')
async def get_file(path: str):
    return {"path": path}

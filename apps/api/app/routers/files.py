from fastapi import APIRouter

try:
    from packages.py_utils.storage import get_presigned_url  # type: ignore
except Exception:  # pragma: no cover - fallback para ambientes sem pacote instalado
    def get_presigned_url(path: str) -> str:  # type: ignore
        return f"https://example.com/{path}"

router = APIRouter()


@router.get('/files/{path:path}')
async def get_file(path: str) -> dict:
    url = get_presigned_url(path)
    return {"url": url}

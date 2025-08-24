"""Endpoints para registrar e acessar artefatos."""
from fastapi import APIRouter
from ..models_artifacts import Artifact, ArtifactCreate

router = APIRouter()


@router.post("/artifacts", response_model=Artifact)
async def create_artifact(art: ArtifactCreate) -> Artifact:
    # Persistência real virá depois
    return Artifact(id="fake-id", path=art.path)


@router.get("/artifacts/{artifact_id}", response_model=Artifact)
async def get_artifact(artifact_id: str) -> Artifact:
    return Artifact(id=artifact_id, path=f"artifacts/{artifact_id}")


@router.get("/artifacts/{artifact_id}/url")
async def get_artifact_url(artifact_id: str) -> dict:
    return {"id": artifact_id, "url": f"https://example.com/{artifact_id}"}

"""Modelos Pydantic para artefatos."""
from pydantic import BaseModel


class Artifact(BaseModel):
    id: str
    path: str


class ArtifactCreate(BaseModel):
    path: str

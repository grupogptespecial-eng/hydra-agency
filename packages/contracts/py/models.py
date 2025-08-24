from pydantic import BaseModel


class AnalysisRequest(BaseModel):
    run_id: str


class Dataset(BaseModel):
    path: str
    coverage: str | None = None


class BacktestReport(BaseModel):
    difference: float


class IngestLineage(BaseModel):
    source: str
    checksum: str | None = None


class DQReport(BaseModel):
    checked: int
    issues: int


class XBRLOutput(BaseModel):
    path: str
    facts: int | None = None

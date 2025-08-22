from pydantic import BaseModel

class AnalysisRequest(BaseModel):
    run_id: str

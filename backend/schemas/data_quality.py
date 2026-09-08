from pydantic import BaseModel, Field


class DataQualityIssue(BaseModel):
    dataset: str
    record_id: str | None = None
    issue_type: str
    severity: str
    message: str


class DataQualityDatasetResult(BaseModel):
    total_records: int
    valid_records: int
    warnings: int
    errors: int


class DataQualityResponse(BaseModel):
    quality_score: float = Field(ge=0, le=100)

    total_records: int = Field(ge=0)

    valid_records: int = Field(ge=0)

    warnings: int = Field(ge=0)

    errors: int = Field(ge=0)

    datasets: dict[str, DataQualityDatasetResult]

    issue_summary: dict[str, int]

    issues: list[DataQualityIssue]
from pydantic import BaseModel

class VersionCheckResponse(BaseModel):
    match: bool
    required_version: str | None = None

class VersionSettingsUpdate(BaseModel):
    version: str

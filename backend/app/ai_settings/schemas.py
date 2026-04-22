from pydantic import BaseModel, Field


class AISettingsRead(BaseModel):
    provider: str
    model: str | None
    anthropic_configured: bool
    openai_configured: bool
    google_configured: bool
    deepseek_configured: bool


class AISettingsUpdate(BaseModel):
    provider: str | None = Field(None, max_length=50)
    model: str | None = Field(None, max_length=100)
    anthropic_api_key: str | None = Field(None, max_length=500)
    openai_api_key: str | None = Field(None, max_length=500)
    google_api_key: str | None = Field(None, max_length=500)
    deepseek_api_key: str | None = Field(None, max_length=500)

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

class TranslateSettings(BaseModel):
    # translate 관련 argument 관리
    max_retry_count: int = 1
    enable_safeguard: bool = True
    enable_qc: bool = True

class Settings(BaseSettings):
    # argument 전달
    translate: TranslateSettings = TranslateSettings()

settings = Settings()
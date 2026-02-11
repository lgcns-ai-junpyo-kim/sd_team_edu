from pydantic_settings import BaseSettinngs, SettingsConfigDict

class Settings(BaseSettings):
    # arguments 관리
    translate_max_retry_count: int = 1
    translate_enable_safeguard: bool = True
    translate_enable_qc: bool = True

settings = Settings()
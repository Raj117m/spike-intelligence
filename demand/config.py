"""Central config. Reads from environment / .env (see .env.example)."""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # storage
    db_path: Path = Path("data/demand.duckdb")

    # synthetic data
    seed: int = 1

    # spike detector params (used by Claude Code in Prompt 2)
    spike_k: float = 3.0          # robust sigma threshold
    spike_min_days: int = 2       # sustained days
    detector_version: str = "v0"

    # optional real-API keys (used in Prompt 5) - left blank by default
    keepa_api_key: str | None = None


settings = Settings()

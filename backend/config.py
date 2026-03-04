from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseModel):
    postgres_db: str = os.getenv("POSTGRES_DB", "floodpulse")
    postgres_user: str = os.getenv("POSTGRES_USER", "floodpulse")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "floodpulse")
    postgres_host: str = os.getenv("POSTGRES_HOST", "db")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    provider: str = os.getenv("PROVIDER", "mock")
    poll_interval_seconds: int = int(os.getenv("POLL_INTERVAL_SECONDS", "600"))
    trend_epsilon_level: float = float(os.getenv("TREND_EPSILON_LEVEL", "0.01"))
    rising_fast_threshold_level_per_hr: float = float(os.getenv("RISING_FAST_THRESHOLD_LEVEL_PER_HR", "0.05"))
    app_timezone: str = os.getenv("APP_TIMEZONE", "Australia/Brisbane")

    @property
    def dsn(self) -> str:
        return (
            f"dbname={self.postgres_db} user={self.postgres_user} "
            f"password={self.postgres_password} host={self.postgres_host} port={self.postgres_port}"
        )


settings = Settings()

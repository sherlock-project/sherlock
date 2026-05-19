from dataclasses import dataclass


@dataclass
class Settings:
    app_name: str = "Beyond The Naked Eye"
    ethical_warning: str = "Public OSINT only. No unauthorized access. Respect laws and ToS."
    database_url: str = "sqlite:///database/bne.db"
    redis_url: str = "redis://localhost:6379/0"


SETTINGS = Settings()

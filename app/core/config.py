from __future__ import annotations

import os
from dataclasses import dataclass, field

DEFAULT_DSN = "postgresql://postgres:postgres@127.0.0.1:5432/sber_portfolio"


@dataclass(frozen=True)
class Settings:
    dsn: str = field(default_factory=lambda: os.getenv("DATABASE_URL", DEFAULT_DSN))
    title: str = "1С · портфель решений"
    company: str = "Внутренние учётные системы"
    pg_bin: str = field(default_factory=lambda: os.getenv("PG_BIN", ""))
    llm_base_url: str = field(default_factory=lambda: os.getenv("LLM_BASE_URL", ""))
    llm_model: str = field(default_factory=lambda: os.getenv("LLM_MODEL", "gpt-4o-mini"))

    @property
    def llm_enabled(self) -> bool:
        return bool(self.llm_base_url)


settings = Settings()

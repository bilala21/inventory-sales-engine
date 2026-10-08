from __future__ import annotations

from enum import StrEnum
from functools import lru_cache

from pydantic import EmailStr, Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApprovalMode(StrEnum):
    REVIEW = "REVIEW"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    database_url: str = "postgresql+psycopg://inventory_sales:inventory_sales@localhost:5432/inventory_sales"
    outreach_enabled: bool = False
    emergency_stop: bool = True
    approval_mode: ApprovalMode = ApprovalMode.REVIEW

    max_new_emails_per_day: int = Field(default=20, ge=0, le=20)
    max_total_emails_per_day: int = Field(default=40, ge=0, le=40)
    max_qualified_companies: int = Field(default=100, ge=1, le=100)
    minimum_fit_score: int = Field(default=70, ge=0, le=100)
    minimum_research_confidence: int = Field(default=70, ge=0, le=100)
    monthly_api_budget_usd: float = Field(default=100.0, ge=0)

    sender_name: str = ""
    sender_email: EmailStr | None = None
    physical_postal_address: str = ""
    booking_link: HttpUrl | None = None

    google_places_api_key: str = ""
    gmail_oauth_client_id: str = ""
    gmail_oauth_client_secret: str = ""
    gmail_oauth_refresh_token: str = ""
    email_verification_api_key: str = ""
    llm_api_key: str = ""
    booking_api_key: str = ""

    def send_readiness_errors(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.outreach_enabled:
            errors.append("outreach_disabled")
        if self.emergency_stop:
            errors.append("emergency_stop_active")
        if self.approval_mode is not ApprovalMode.REVIEW:
            errors.append("review_mode_required")
        if not self.sender_name.strip():
            errors.append("sender_name_missing")
        if self.sender_email is None:
            errors.append("sender_email_missing")
        if not self.physical_postal_address.strip():
            errors.append("physical_postal_address_missing")
        if self.booking_link is None:
            errors.append("booking_link_missing")
        return tuple(errors)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

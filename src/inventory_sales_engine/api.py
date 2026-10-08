from __future__ import annotations

from fastapi import FastAPI

from inventory_sales_engine.config import Settings, get_settings
from inventory_sales_engine.metrics.service import VALIDATION_TARGETS


def create_app(settings: Settings | None = None) -> FastAPI:
    configured = settings or get_settings()
    app = FastAPI(title="Inventory Sales Engine", version="0.1.0")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/safety/status")
    def safety_status() -> dict[str, str | bool | int]:
        return {
            "approval_mode": configured.approval_mode.value,
            "outreach_enabled": configured.outreach_enabled,
            "emergency_stop": configured.emergency_stop,
            "max_new_emails_per_day": configured.max_new_emails_per_day,
            "max_total_emails_per_day": configured.max_total_emails_per_day,
            "max_qualified_companies": configured.max_qualified_companies,
        }

    @app.get("/validation-targets")
    def validation_targets() -> dict[str, int]:
        return dict(VALIDATION_TARGETS)

    return app


app = create_app()


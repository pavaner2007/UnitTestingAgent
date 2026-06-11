from datetime import datetime
from sqlalchemy import DateTime, String, Text, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class AnalysisReportModel(Base):
    __tablename__ = "analysis_reports"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    repository_name: Mapped[str] = mapped_column(String(255), nullable=False)
    repository_url: Mapped[str] = mapped_column(Text, nullable=False)
    report_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

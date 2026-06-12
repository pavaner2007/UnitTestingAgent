from sqlalchemy.orm import Session

from app.db.models import AnalysisReportModel


class AnalysisRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, analysis_id: str, repository_name: str, repository_url: str, report_json: dict) -> AnalysisReportModel:
        model = AnalysisReportModel(
            id=analysis_id,
            repository_name=repository_name,
            repository_url=repository_url,
            report_json=report_json,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

    def get_by_id(self, analysis_id: str) -> AnalysisReportModel | None:
        return self.db.query(AnalysisReportModel).filter(AnalysisReportModel.id == analysis_id).first()

    def list_all(self, limit: int = 50) -> list[AnalysisReportModel]:
        """Return up to `limit` analyses ordered newest first."""
        return (
            self.db.query(AnalysisReportModel)
            .order_by(AnalysisReportModel.created_at.desc())
            .limit(limit)
            .all()
        )

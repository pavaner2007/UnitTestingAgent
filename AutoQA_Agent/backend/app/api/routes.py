import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io

from app.core.config import settings
from app.core.exceptions import AnalysisNotFoundException, AutoQAException
from app.db.session import get_db
from app.schemas.analysis import (
    AnalyzeRepositoryRequest,
    AnalyzeRepositoryResponse,
    HealthResponse,
    RepositoryAnalysisReport,
)
from app.services.analysis_service import RepositoryAnalysisService
from app.services.pdf_service import generate_pdf

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["System"])
def health_check() -> HealthResponse:
    return HealthResponse(status="healthy", service=settings.app_name)


@router.post("/analyze-repository", response_model=AnalyzeRepositoryResponse, tags=["Analysis"])
def analyze_repository(payload: AnalyzeRepositoryRequest, db: Session = Depends(get_db)) -> AnalyzeRepositoryResponse:
    try:
        service = RepositoryAnalysisService(db)
        report = service.analyze_repository(str(payload.github_url))
        return AnalyzeRepositoryResponse(analysis_id=report.analysis_id, status="completed", report=report)
    except AutoQAException as exc:
        logger.exception("Repository analysis failed")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Unexpected analysis error")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error") from exc


@router.get("/analysis/{analysis_id}", tags=["Analysis"])
def get_analysis(analysis_id: str, db: Session = Depends(get_db)) -> dict:
    try:
        service = RepositoryAnalysisService(db)
        return service.get_analysis(analysis_id)
    except AnalysisNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/analyses", tags=["Analysis"])
def list_analyses(limit: int = 50, db: Session = Depends(get_db)) -> list:
    """Return a summary list of all past analyses, newest first."""
    service = RepositoryAnalysisService(db)
    return service.get_analyses(limit=limit)


@router.get("/analysis/{analysis_id}/pdf", tags=["Analysis"])
def download_pdf(analysis_id: str, db: Session = Depends(get_db)):
    """Generate and stream a PDF report for the given analysis ID."""
    try:
        service = RepositoryAnalysisService(db)
        report_data = service.get_analysis(analysis_id)
        report = RepositoryAnalysisReport(**report_data)
        pdf_bytes = generate_pdf(report)
        filename = f"autoqa-{report.repository_name}-{analysis_id[:8]}.pdf"
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except AnalysisNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("PDF generation failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="PDF generation failed") from exc

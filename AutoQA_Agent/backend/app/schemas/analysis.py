from typing import Any
from pydantic import BaseModel, Field, HttpUrl


class AnalyzeRepositoryRequest(BaseModel):
    github_url: HttpUrl = Field(..., description="Public GitHub repository URL")


class ApiEndpoint(BaseModel):
    method: str
    path: str
    framework: str
    file: str
    line_number: int | None = None
    function_name: str | None = None


class TechStackResponse(BaseModel):
    frontend: list[str] = []
    backend: list[str] = []
    languages: list[str] = []
    databases: list[str] = []
    frameworks: list[str] = []
    package_managers: list[str] = []
    raw_evidence: dict[str, list[str]] = {}


class ProjectStructureSummary(BaseModel):
    directories: int
    files: int
    top_level_items: list[str]
    important_files: list[str]


class DetectedFeature(BaseModel):
    """A feature detected from code evidence (never inferred from repo name)."""
    name: str
    evidence: list[str] = []  # e.g. ["POST /login", "auth middleware", "routes/auth.js"]


class RepositoryAnalysisReport(BaseModel):
    analysis_id: str
    repository_name: str
    repository_url: str
    metadata: dict[str, Any]
    technology_stack: TechStackResponse
    project_structure_summary: ProjectStructureSummary
    number_of_files: int
    number_of_apis_discovered: int
    api_inventory: list[ApiEndpoint]

    # Ollama-generated summaries
    readme_summary: str | None = None
    module_summaries: dict[str, str] = {}  # module_name → summary

    # Groq-generated analysis (from structured facts only)
    ai_explanation: dict[str, Any] | None = None
    detected_features: list[DetectedFeature] = []
    architecture_notes: str | None = None
    workflow: list[str] = []
    confidence_score: float | None = None  # 0–100


class AnalyzeRepositoryResponse(BaseModel):
    analysis_id: str
    status: str
    report: RepositoryAnalysisReport


class HealthResponse(BaseModel):
    status: str
    service: str

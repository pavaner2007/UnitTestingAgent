"""
RepositoryAnalysisService — orchestrates the full Code-First → Ollama → Groq pipeline.

Pipeline:
  1. Clone repository
  2. Deterministic tech stack detection (TechStackDetectionAgent)
  3. Deterministic API discovery (ApiDiscoveryAgent)
  4. Read README → Ollama summarisation
  5. Detect top-level modules → Ollama module summarisation
  6. Build structured_facts (no raw code, only facts)
  7. Groq reasoning on structured facts → enriched analysis
  8. Assemble final RepositoryAnalysisReport
  9. Persist to DB + JSON file
"""
import logging
from pathlib import Path

from sqlalchemy.orm import Session

from app.agents.api_discovery_agent import ApiDiscoveryAgent
from app.agents.report_generation_agent import ReportGenerationAgent
from app.agents.repository_analysis_agent import RepositoryAnalysisAgent
from app.agents.tech_stack_agent import TechStackDetectionAgent
from app.core.exceptions import AnalysisNotFoundException
from app.repositories.analysis_repository import AnalysisRepository
from app.schemas.analysis import DetectedFeature, RepositoryAnalysisReport
from app.services.groq_service import GroqAnalysisService
from app.services.ollama_service import OllamaService

logger = logging.getLogger(__name__)

# Directories that are not meaningful top-level modules
_IGNORED_TOP_LEVEL = {
    ".git", "node_modules", "venv", ".venv", "dist", "build",
    "target", "__pycache__", ".github", ".idea", ".vscode",
    "coverage", ".pytest_cache", "htmlcov",
}

# README file name variants to look for
_README_NAMES = {"README.md", "README.rst", "README.txt", "README", "readme.md"}


class RepositoryAnalysisService:
    def __init__(self, db: Session) -> None:
        self.repository_agent = RepositoryAnalysisAgent()
        self.tech_stack_agent = TechStackDetectionAgent()
        self.api_discovery_agent = ApiDiscoveryAgent()
        self.report_generation_agent = ReportGenerationAgent()
        self.analysis_repository = AnalysisRepository(db)
        self.ollama = OllamaService()
        self.groq = GroqAnalysisService()

    # ── Public API ────────────────────────────────────────────────────────────

    def analyze_repository(self, github_url: str) -> RepositoryAnalysisReport:
        logger.info("Starting repository analysis for %s", github_url)

        # ── Step 1-3: Deterministic analysis ────────────────────────────────
        local_path = self.repository_agent.clone_repository(github_url)
        metadata = self.repository_agent.extract_metadata(github_url, local_path)
        tech_stack = self.tech_stack_agent.detect(local_path)
        api_inventory = self.api_discovery_agent.discover(local_path)

        # ── Step 4: README summarisation via Ollama ──────────────────────────
        readme_summary = self._summarize_readme(local_path)

        # ── Step 5: Module summarisation via Ollama ──────────────────────────
        module_summaries = self._summarize_modules(local_path)

        # ── Step 6: Build structured facts (no raw code) ────────────────────
        structured_facts = {
            "repository_name": metadata.repository_name,
            "frontend": tech_stack.frontend,
            "backend": tech_stack.backend,
            "databases": tech_stack.databases,
            "languages": tech_stack.languages,
            "frameworks": tech_stack.frameworks,
            "apis": [
                {
                    "method": ep.method,
                    "path": ep.path,
                    "framework": ep.framework,
                    "file": ep.file,
                }
                for ep in api_inventory
            ],
            "modules": [
                {"name": name, "summary": summary}
                for name, summary in module_summaries.items()
                if summary
            ],
            "readme_summary": readme_summary,
            "important_files": metadata.important_files[:15],
            "total_files": metadata.total_files,
            "total_dirs": metadata.total_directories,
        }

        # ── Step 7: Groq high-level reasoning ───────────────────────────────
        logger.info("Sending structured facts to Groq for reasoning")
        ai_result = self.groq.generate_report(structured_facts)

        # ── Step 8: Assemble final report ────────────────────────────────────
        base_report = self.report_generation_agent.generate(
            metadata, tech_stack, api_inventory
        )

        # Parse detected_features from Groq output
        detected_features = [
            DetectedFeature(
                name=f.get("name", "Unknown"),
                evidence=f.get("evidence", []),
            )
            for f in ai_result.get("detected_features", [])
            if isinstance(f, dict)
        ]

        report = base_report.model_copy(
            update={
                "readme_summary": readme_summary,
                "module_summaries": module_summaries,
                "ai_explanation": {
                    "project_overview": ai_result.get("project_overview"),
                    "use_case": ai_result.get("use_case"),
                    "complexity_level": ai_result.get("complexity_level"),
                    "workflow": ai_result.get("workflow", []),
                    "key_technologies": ai_result.get("key_technologies", {}),
                    "api_summary": ai_result.get("api_summary"),
                },
                "detected_features": detected_features,
                "architecture_notes": ai_result.get("architecture_notes"),
                "workflow": ai_result.get("workflow", []),
                "confidence_score": ai_result.get("confidence_score"),
            }
        )

        # ── Step 9: Persist ──────────────────────────────────────────────────
        self.report_generation_agent.save_json_report(report)
        self.analysis_repository.save(
            analysis_id=report.analysis_id,
            repository_name=report.repository_name,
            repository_url=report.repository_url,
            report_json=report.model_dump(),
        )
        logger.info(
            "Analysis complete: %s (confidence: %.0f%%)",
            report.analysis_id,
            report.confidence_score or 0,
        )
        return report

    def get_analysis(self, analysis_id: str) -> dict:
        model = self.analysis_repository.get_by_id(analysis_id)
        if not model:
            raise AnalysisNotFoundException(f"Analysis not found: {analysis_id}")
        return model.report_json

    def get_analyses(self, limit: int = 50) -> list[dict]:
        """Return a lightweight summary list of all past analyses (newest first)."""
        rows = self.analysis_repository.list_all(limit=limit)
        results = []
        for row in rows:
            rj = row.report_json or {}
            results.append({
                "analysis_id":      row.id,
                "repository_name":  row.repository_name,
                "repository_url":   row.repository_url,
                "created_at":       row.created_at.isoformat() if row.created_at else None,
                "confidence_score": rj.get("confidence_score"),
                "technology_stack": rj.get("technology_stack", {}),
                "number_of_files":  rj.get("number_of_files"),
                "number_of_apis_discovered": rj.get("number_of_apis_discovered"),
            })
        return results


    # ── Private helpers ───────────────────────────────────────────────────────

    def _summarize_readme(self, repo_path: Path) -> str | None:
        """Find and summarise the README via Ollama."""
        for name in _README_NAMES:
            readme_path = repo_path / name
            if readme_path.exists() and readme_path.is_file():
                try:
                    text = readme_path.read_text(encoding="utf-8", errors="ignore")
                    if text.strip():
                        logger.info("Summarising README via Ollama (%d chars)", len(text))
                        return self.ollama.summarize_readme(text)
                except Exception as exc:
                    logger.warning("Failed to read README: %s", exc)
        logger.info("No README found in repository root")
        return None

    def _summarize_modules(self, repo_path: Path) -> dict[str, str]:
        """
        Detect top-level directories as modules and summarise each via Ollama.
        Only processes directories with source files; skips tooling/config dirs.
        """
        summaries: dict[str, str] = {}
        try:
            top_level_dirs = [
                p for p in repo_path.iterdir()
                if p.is_dir() and p.name not in _IGNORED_TOP_LEVEL
            ]
        except Exception:
            return summaries

        for module_dir in sorted(top_level_dirs)[:12]:  # cap at 12 modules
            try:
                file_names = [
                    f.name for f in module_dir.rglob("*")
                    if f.is_file() and f.name not in {"__pycache__"}
                    and not any(part in _IGNORED_TOP_LEVEL for part in f.parts)
                ][:40]

                if not file_names:
                    continue

                logger.info("Summarising module '%s' via Ollama", module_dir.name)
                summary = self.ollama.summarize_module(module_dir.name, file_names)
                if summary:
                    summaries[module_dir.name] = summary
            except Exception as exc:
                logger.warning("Module summarisation failed for %s: %s", module_dir.name, exc)

        return summaries

from fastapi import APIRouter
from app.schemas import AnalysisResult, MatchRequest, ExportRequest
from app.services.skill_extractor import get_skill_extractor
from app.services.embedding_matcher import get_embedding_matcher
from app.services.scoring import ScoringEngine
from app.services.llm_analyzer import LLMAnalyzer
from app.services.exporter import to_markdown
from fastapi.responses import PlainTextResponse

router = APIRouter(tags=["Match"])

_llm_analyzer = LLMAnalyzer()


@router.post("/match", response_model=AnalysisResult)
async def match(request: MatchRequest) -> AnalysisResult:
    extractor = get_skill_extractor()
    matcher = get_embedding_matcher()
    engine = ScoringEngine(extractor, matcher)

    result = engine.score(request.cv_text, request.job_descriptions)

    if request.use_llm:
        result = _llm_analyzer.enrich(result, request.cv_text, request.job_descriptions)
    else:
        result = _llm_analyzer._deterministic_enrich(result, request.cv_text)

    return result


@router.post("/analysis/export-markdown", response_class=PlainTextResponse)
async def export_markdown(request: ExportRequest) -> str:
    return to_markdown(request.analysis, request.cv_name, request.job_title)

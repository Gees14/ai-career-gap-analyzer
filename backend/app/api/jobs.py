from fastapi import APIRouter
from app.schemas import JobAnalyzeRequest, JobParseResult
from app.services.skill_extractor import get_skill_extractor
from app.services.job_parser import JobParser

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("/analyze", response_model=list[JobParseResult])
async def analyze_jobs(request: JobAnalyzeRequest) -> list[JobParseResult]:
    extractor = get_skill_extractor()
    parser = JobParser(extractor)
    return [parser.parse(jd) for jd in request.job_descriptions]

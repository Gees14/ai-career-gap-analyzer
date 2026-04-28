from fastapi import APIRouter
from app.services.skill_extractor import get_skill_extractor

router = APIRouter(prefix="/skills", tags=["Skills"])


@router.get("/taxonomy")
async def get_taxonomy() -> dict[str, list[str]]:
    extractor = get_skill_extractor()
    return extractor.get_taxonomy()

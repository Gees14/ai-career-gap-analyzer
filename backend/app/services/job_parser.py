"""Job description parser: extracts structured requirements from raw text."""
import re
from app.core.logging import get_logger
from app.schemas import JobParseResult
from app.services.skill_extractor import SkillExtractor

logger = get_logger(__name__)

_REQUIRED_MARKERS = re.compile(
    r"(?i)(required|must have|requirements?|you (will|must|should) (have|know|bring)|"
    r"minimum qualifications?|basic qualifications?)",
)
_PREFERRED_MARKERS = re.compile(
    r"(?i)(preferred|nice to have|bonus|plus|advantageous|desirable|"
    r"additional qualifications?)",
)
_YEARS_PATTERN = re.compile(r"(\d+)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?experience")
_SOFT_SKILL_TERMS = {
    "communication", "teamwork", "collaboration", "leadership", "problem solving",
    "critical thinking", "adaptability", "time management", "presentation",
    "cross-functional", "stakeholder",
}


class JobParser:
    def __init__(self, extractor: SkillExtractor) -> None:
        self._extractor = extractor

    def parse(self, text: str) -> JobParseResult:
        years = self._extract_years(text)
        soft_skills = self._extract_soft_skills(text)

        required_block, preferred_block = self._split_required_preferred(text)

        required_matches = self._extractor.extract(required_block or text)
        preferred_matches = self._extractor.extract(preferred_block) if preferred_block else []

        required_skills = list({m.skill for m in required_matches})
        preferred_skills = list({m.skill for m in preferred_matches} - set(required_skills))

        category_map: dict[str, list[str]] = {
            "Cloud": [],
            "MLOps": [],
            "Generative AI": [],
            "Software Engineering": [],
            "Backend APIs": [],
        }
        for m in required_matches + preferred_matches:
            if m.category in category_map:
                if m.skill not in category_map[m.category]:
                    category_map[m.category].append(m.skill)

        return JobParseResult(
            raw_text=text,
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            tools_frameworks=self._extract_tools(text),
            cloud_requirements=category_map["Cloud"],
            mlops_requirements=category_map["MLOps"],
            genai_requirements=category_map["Generative AI"],
            software_engineering=category_map["Software Engineering"] + category_map["Backend APIs"],
            soft_skills=list(soft_skills),
            years_experience=years,
        )

    # ------------------------------------------------------------------
    def _split_required_preferred(self, text: str) -> tuple[str, str]:
        req_match = _REQUIRED_MARKERS.search(text)
        pref_match = _PREFERRED_MARKERS.search(text)

        if not req_match:
            return text, ""

        req_start = req_match.start()
        if pref_match and pref_match.start() > req_start:
            return text[req_start:pref_match.start()], text[pref_match.start():]
        return text[req_start:], ""

    def _extract_years(self, text: str) -> int | None:
        matches = _YEARS_PATTERN.findall(text)
        if matches:
            return max(int(y) for y in matches)
        return None

    def _extract_soft_skills(self, text: str) -> set[str]:
        lower = text.lower()
        return {s for s in _SOFT_SKILL_TERMS if s in lower}

    def _extract_tools(self, text: str) -> list[str]:
        tool_patterns = [
            r"\bpython\b", r"\bpytorch\b", r"\btensorflow\b", r"\bkeras\b",
            r"\bdocker\b", r"\bkubernetes\b", r"\bmlflow\b", r"\bfastapi\b",
            r"\bhugging\s*face\b", r"\blangchain\b", r"\bchromadb\b", r"\bpinecone\b",
            r"\bfaiss\b", r"\bqdrant\b", r"\bspark\b", r"\bkafka\b",
            r"\bairflow\b", r"\bterraform\b", r"\baws\b", r"\bgcp\b", r"\bazure\b",
        ]
        found = []
        lower = text.lower()
        for p in tool_patterns:
            if re.search(p, lower):
                name = re.sub(r"\\b|\\s\*", " ", p).strip()
                found.append(name.replace("\\b", "").strip())
        return found

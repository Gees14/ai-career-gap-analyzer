"""Skill extractor: matches taxonomy skills and synonyms against text."""
import re
from functools import lru_cache
from pathlib import Path

import yaml

from app.core.logging import get_logger
from app.schemas import SkillMatch

logger = get_logger(__name__)

_TAXONOMY_PATH = Path(__file__).parent.parent.parent / "configs" / "skills_taxonomy.yaml"


class SkillExtractor:
    """Deterministic keyword-based skill extractor backed by a YAML taxonomy."""

    def __init__(self, taxonomy_path: Path = _TAXONOMY_PATH) -> None:
        self._taxonomy = self._load_taxonomy(taxonomy_path)
        # Flat lookup: normalised term → (canonical_skill, category)
        self._term_index: dict[str, tuple[str, str]] = {}
        self._build_index()

    # ------------------------------------------------------------------
    def extract(self, text: str) -> list[SkillMatch]:
        """Return all skills found in *text*, deduplicated by canonical name."""
        if not text:
            return []

        lower = text.lower()
        found: dict[str, SkillMatch] = {}

        for term, (skill, category) in self._term_index.items():
            # Word-boundary aware search; term may contain spaces
            pattern = r"(?<!\w)" + re.escape(term) + r"(?!\w)"
            match = re.search(pattern, lower)
            if match:
                if skill not in found:
                    evidence = self._get_evidence(text, match.start(), match.end())
                    found[skill] = SkillMatch(
                        skill=skill,
                        category=category,
                        evidence=evidence,
                        similarity_score=1.0,
                    )

        return list(found.values())

    def get_taxonomy(self) -> dict[str, list[str]]:
        """Return {category: [canonical_skills]} for the API taxonomy endpoint."""
        result: dict[str, list[str]] = {}
        for category, entries in self._taxonomy.items():
            result[category] = [e["skill"] for e in entries]
        return result

    # ------------------------------------------------------------------
    def _load_taxonomy(self, path: Path) -> dict:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data.get("skills", {})

    def _build_index(self) -> None:
        for category, entries in self._taxonomy.items():
            for entry in entries:
                skill = entry["skill"]
                # Index the canonical name itself
                self._term_index[skill.lower()] = (skill, category)
                for synonym in entry.get("synonyms", []):
                    self._term_index[synonym.lower()] = (skill, category)

    @staticmethod
    def _get_evidence(text: str, start: int, end: int, window: int = 80) -> str:
        """Return surrounding context as evidence snippet."""
        s = max(0, start - window)
        e = min(len(text), end + window)
        snippet = text[s:e].replace("\n", " ").strip()
        return f"...{snippet}..." if s > 0 else snippet


@lru_cache(maxsize=1)
def get_skill_extractor() -> SkillExtractor:
    return SkillExtractor()

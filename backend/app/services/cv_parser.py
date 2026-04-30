"""CV parser: extracts raw text and sections from PDF or plain text."""
import io
import re
from pathlib import Path

from app.core.logging import get_logger
from app.schemas import CVParseResult

logger = get_logger(__name__)

_SECTION_PATTERNS: dict[str, list[str]] = {
    "summary": [
        r"(?i)(professional\s+summary|summary|profile|about\s+me|objective)\s*[:\-]?",
    ],
    "experience": [
        r"(?i)(work\s+experience|experience|employment|professional\s+experience|career\s+history)\s*[:\-]?",
    ],
    "projects": [
        r"(?i)(projects?|personal\s+projects?|key\s+projects?|selected\s+projects?)\s*[:\-]?",
    ],
    "skills": [
        r"(?i)(technical\s+skills?|skills?\s+&\s+tools|skills?|competencies|expertise|technologies)\s*[:\-]?\s*\n",
        r"(?i)^(technical\s+skills?|skills?|competencies|expertise|technologies)\s*$",
    ],
    "education": [
        r"(?i)(education|academic\s+background|qualifications?|degrees?)\s*[:\-]?",
    ],
    "certifications": [
        r"(?i)(certifications?|certificates?|credentials?|accreditations?)\s*[:\-]?",
    ],
}

# Order matters — used to detect where each section ends
_SECTION_ORDER = ["summary", "experience", "projects", "skills", "education", "certifications"]


def parse_cv_text(text: str) -> CVParseResult:
    """Parse plain text CV into structured sections."""
    sections = _extract_sections(text)
    return CVParseResult(
        raw_text=text,
        summary=sections.get("summary", ""),
        experience=sections.get("experience", ""),
        projects=sections.get("projects", ""),
        skills=sections.get("skills", ""),
        education=sections.get("education", ""),
        certifications=sections.get("certifications", ""),
    )


def parse_cv_pdf(file_bytes: bytes) -> CVParseResult:
    """Extract text from a PDF file and parse sections."""
    text = _extract_pdf_text(file_bytes)
    if not text.strip():
        logger.warning("PDF produced empty text — returning empty result")
        return CVParseResult(raw_text="")
    return parse_cv_text(text)


def _extract_pdf_text(file_bytes: bytes) -> str:
    """Try pdfplumber first, fall back to pypdf."""
    try:
        import pdfplumber

        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages = [p.extract_text() or "" for p in pdf.pages]
        return "\n".join(pages)
    except Exception as exc:
        logger.warning("pdfplumber failed (%s), trying pypdf", exc)

    try:
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(file_bytes))
        return "\n".join(p.extract_text() or "" for p in reader.pages)
    except Exception as exc:
        logger.error("pypdf also failed: %s", exc)
        return ""


def _extract_sections(text: str) -> dict[str, str]:
    """Heuristically split CV text into named sections."""
    # Build a flat list of (start_pos, section_name) tuples
    hits: list[tuple[int, str]] = []
    for section, patterns in _SECTION_PATTERNS.items():
        for pattern in patterns:
            for m in re.finditer(pattern, text):
                hits.append((m.start(), section))

    if not hits:
        # Cannot find any section headers — store everything as raw experience
        return {"experience": text}

    # Sort by position and keep only the first hit per section
    hits.sort(key=lambda x: x[0])
    seen: set[str] = set()
    ordered: list[tuple[int, str]] = []
    for pos, name in hits:
        if name not in seen:
            seen.add(name)
            ordered.append((pos, name))

    sections: dict[str, str] = {}
    for i, (pos, name) in enumerate(ordered):
        end = ordered[i + 1][0] if i + 1 < len(ordered) else len(text)
        # Strip the header line itself
        content = text[pos:end]
        content = re.sub(_SECTION_PATTERNS[name][0], "", content, count=1)
        sections[name] = content.strip()

    return sections

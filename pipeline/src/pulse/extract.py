"""Skill extraction: job text -> set of canonical skill slugs."""
from __future__ import annotations

from .taxonomy import COMPILED


def extract_skills(text: str) -> set[str]:
    """Match the taxonomy against title + description text.

    Pure and deterministic — same text in, same skills out. Adzuna truncates
    descriptions (~500 chars), so this undercounts skills mentioned late in an
    ad; that's a stated limitation, applied uniformly across all postings.
    """
    if not text:
        return set()
    return {slug for slug, rx in COMPILED.items() if rx.search(text)}

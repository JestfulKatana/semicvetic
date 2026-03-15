from __future__ import annotations

from flask import request


def build_org_schema(settings: dict[str, str]) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": ["EducationalOrganization", "LocalBusiness"],
        "name": settings.get("site_name", "Семицветик"),
        "telephone": settings.get("phone_1", ""),
        "address": settings.get("address", ""),
        "url": settings.get("site_url", request.url_root.rstrip("/")),
        "description": settings.get("site_description", ""),
    }


def build_course_schema(program) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "Course",
        "name": program.name,
        "description": program.tagline or program.description,
        "provider": {"@type": "EducationalOrganization", "name": "Семицветик"},
    }

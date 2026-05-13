from __future__ import annotations

from flask import request


def build_org_schema(settings: dict[str, str]) -> dict:
    """Schema.org микроразметка только из подтверждённых данных в site_settings.

    Не добавляем aggregateRating/foundingDate/openingHours/geo, пока эти
    значения не подтверждены через site_settings (нельзя выдумывать рейтинги,
    даты основания, часы работы — это вводит пользователя в заблуждение в
    поисковой выдаче).
    """
    base_url = settings.get("site_url") or request.url_root.rstrip("/")
    same_as = [u for u in (
        settings.get("social_vk"),
        settings.get("social_tg"),
        settings.get("social_max"),
    ) if u]
    schema: dict = {
        "@context": "https://schema.org",
        "@type": ["EducationalOrganization", "ChildCare", "LocalBusiness"],
        "@id": base_url + "/#organization",
        "name": settings.get("site_name", "Семицветик"),
        "alternateName": "Детский центр «Семицветик»",
        "url": base_url,
        "logo": base_url + "/static/img/logo-flower.png",
        "image": base_url + "/static/img/og-default.jpg",
        "areaServed": {"@type": "City", "name": "Сергиев Посад"},
    }
    if settings.get("phone_1"):
        schema["telephone"] = settings["phone_1"]
    if settings.get("site_description"):
        schema["description"] = settings["site_description"]
    if settings.get("address"):
        schema["address"] = {
            "@type": "PostalAddress",
            "addressLocality": "Сергиев Посад",
            "addressRegion": "Московская область",
            "addressCountry": "RU",
            "streetAddress": settings["address"],
        }
    # Опционально, только если задано в БД
    if settings.get("founding_date"):
        schema["foundingDate"] = settings["founding_date"]
    if settings.get("hours_open") and settings.get("hours_close"):
        schema["openingHoursSpecification"] = [{
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
            "opens": settings["hours_open"],
            "closes": settings["hours_close"],
        }]
    if settings.get("rating_value") and settings.get("rating_count"):
        schema["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": settings["rating_value"],
            "reviewCount": settings["rating_count"],
            "bestRating": "5",
            "worstRating": "1",
        }
    if settings.get("geo_lat") and settings.get("geo_lon"):
        schema["geo"] = {
            "@type": "GeoCoordinates",
            "latitude": settings["geo_lat"],
            "longitude": settings["geo_lon"],
        }
    if same_as:
        schema["sameAs"] = same_as
    return schema


def build_course_schema(program) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "Course",
        "name": program.name,
        "description": program.tagline or program.description,
        "provider": {"@type": "EducationalOrganization", "name": "Семицветик"},
    }

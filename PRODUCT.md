# Семицветик — альтернативная версия

## Platform and stack
Web, Flask/Jinja, SQLAlchemy/SQLite, vanilla CSS/JS. Separate branch: `version/site-rebuild`. Existing administration and public URL structure remain. Production has not been deployed or restarted for this work.

## Mandate and concept
On 2026-09-14 the user delegated design and product decisions for a separate version, then clarified that the original concept must remain. The implementation preserves the original multicolored flower, warm cream/amber/orange/violet/green world, real photographs and supplied teacher portraits. This is an authored direction, not a user-research finding or blanket approval of every implementation detail.

## Audience and task
Inferred from the existing center: parents choosing developmental activities, school preparation, language, creative or specialist support for their child in Sergiev Posad. Journey: explore direction → understand activities → meet people → request contact. A request is not a confirmed booking.

## Truth
Teacher names, roles and portraits were supplied by the user. Existing published program names and descriptions establish scope, not guaranteed results. Prices, ages, duration, schedules, places, testimonials, awards and callback promises require confirmation. `SiteSetting.program_terms_verified` defaults to false: program terms remain hidden until the center confirms them. Existing contacts and public photography are inherited; final accuracy and publishing rights remain release checks. No fabricated reviews or generated documentary photos.

Published Event records remain existing editorial content and need review before public launch. An existing published privacy Page is preserved. The fallback “Данные заявки” notice only describes form data and purpose; it is not an approved legal policy.

## Implemented scope and compatibility
Seven core pages, eight program routes, news list/detail and existing article routes share the new page family and one inquiry flow. Program context is stored in `Lead.note`. Custom published Pages beyond the core preserve the original `content_page.html` and `hydrate_blocks` rendering so the JSON block editor contract remains intact. This is a deliberate compatibility boundary, not a claim that every custom page has been redesigned.

## Acceptance and release boundary
Backend contract tests, browser exercises, responsive scans and visual review are recorded in `docs/VERSION_REBUILD.md`. No production forms were submitted for QA. The separate version intentionally carries noindex in its new base template; SEO structured data and indexing require a release review before publication. Existing legal, business and editorial approvals are still required; no production rollout is authorized by the design task.

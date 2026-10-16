"""Faerûn Cartographers branding, applied to every HTML page the server sends.

Pages are built by many separate asset modules, so the logo, favicon and footer
are injected in one place rather than copied into each page.
"""

from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Dict, Tuple

BRAND_NAME = "Faerûn Cartographers"
PRODUCT_NAME = "Faerûn Economy Engine"
COPYRIGHT_YEAR = 2026

STATIC_DIR = Path(__file__).resolve().parent / "static"
LOGO_ALT = f"{BRAND_NAME} logo"

BRAND_BINARY_ASSETS: Dict[str, Tuple[Path, str]] = {
    "faerun-cartographers-32.png": (STATIC_DIR / "faerun-cartographers-32.png", "image/png"),
    "faerun-cartographers-96.png": (STATIC_DIR / "faerun-cartographers-96.png", "image/png"),
    "faerun-cartographers-192.png": (STATIC_DIR / "faerun-cartographers-192.png", "image/png"),
    "favicon.ico": (STATIC_DIR / "favicon.ico", "image/x-icon"),
}

TRADEMARK_NOTICE = (
    "Forgotten Realms, Faerûn, Dungeons &amp; Dragons and related names are trademarks of "
    "Wizards of the Coast LLC. This is unofficial fan content, not approved or endorsed by "
    "Wizards of the Coast. Populations, prices and businesses are simulation values, not "
    "published statistics."
)

BRAND_CSS = """
.fc-mark { display: inline-flex; flex: none; align-items: center; margin-right: 14px; }
.fc-mark img { display: block; width: 84px; height: 84px; }
.atlasbar .fc-mark { margin-right: 4px; }
.atlasbar .fc-mark img { width: 56px; height: 56px; }
html:has(.fc-footer-compact) body:not(.mapbody) { padding-bottom: 26px; }
.fc-footer {
  box-sizing: border-box; clear: both; display: flex; flex-wrap: wrap; align-items: center;
  gap: 10px 28px; margin: 36px 0 0; padding: 20px clamp(16px, 3%, 64px);
  border-top: 1px solid rgba(128, 128, 128, .35); font: 12px/1.6 "Segoe UI", Aptos, Calibri, sans-serif;
  color: inherit; background: transparent;
}
.fc-footer a { color: inherit; text-decoration: underline; text-underline-offset: 2px; }
.fc-footer-brand { display: flex; align-items: center; gap: 12px; flex: none; }
.fc-footer-brand img { display: block; width: 48px; height: 48px; }
.fc-footer-brand strong { display: block; font-size: 14px; letter-spacing: .04em; }
.fc-footer-brand span { display: block; opacity: .75; }
.fc-footer-text { flex: 1 1 420px; min-width: 0; margin: 0; opacity: .82; }
.fc-footer-text p { margin: 0 0 4px; }
.fc-footer-nav { display: flex; flex-wrap: wrap; gap: 6px 16px; }
.fc-footer-compact {
  position: fixed; left: 0; right: 0; bottom: 0; z-index: 15; margin: 0; padding: 3px 16px;
  gap: 4px 18px; flex-wrap: nowrap; overflow: hidden; white-space: nowrap; font-size: 11px; line-height: 1.5;
  background: rgba(252, 251, 248, .94); color: #3a3a3a;
}
html[data-theme="dark"] .fc-footer-compact { background: rgba(40, 40, 40, .94); color: #e6e6e6; }
.fc-footer-compact .fc-footer-brand img { width: 20px; height: 20px; }
.fc-footer-compact .fc-footer-brand span, .fc-footer-compact .fc-footer-nav { display: none; }
.fc-footer-compact .fc-footer-brand { gap: 8px; }
.fc-footer-compact .fc-footer-brand strong { font-size: 11px; display: inline; }
.fc-footer-compact .fc-footer-text { flex: 1 1 auto; overflow: hidden; text-overflow: ellipsis; }
.fc-footer-compact .fc-footer-text p:not(:first-child) { display: none; }
@media (max-width: 720px) {
  .fc-mark img { width: 56px; height: 56px; }
  .fc-footer-compact .fc-footer-text { display: none; }
}
@media print { .fc-footer-compact { position: static; } }
"""

BRAND_ASSETS: Dict[str, Tuple[str, str]] = {
    "brand.css": (BRAND_CSS, "text/css; charset=utf-8"),
}

HEAD_LINKS = (
    '<link rel="icon" type="image/png" sizes="32x32" href="faerun-cartographers-32.png">'
    '<link rel="icon" href="favicon.ico" sizes="any">'
    '<link rel="apple-touch-icon" href="faerun-cartographers-192.png">'
    f'<meta name="application-name" content="{html.escape(PRODUCT_NAME)}">'
    '<link rel="stylesheet" href="brand.css">'
)

LOGO_LINK = (
    f'<a class="fc-mark" href="index.html" aria-label="{html.escape(BRAND_NAME)}: home" '
    f'title="{html.escape(BRAND_NAME)}">'
    f'<img src="faerun-cartographers-192.png" alt="{html.escape(LOGO_ALT)}" width="84" height="84">'
    "</a>"
)

_TITLE = re.compile(r"(<title>)(.*?)(</title>)", re.IGNORECASE | re.DOTALL)
_BRAND_DIV = re.compile(r'<div class="brand"[^>]*>')
_HEADER = re.compile(r"<header\b[^>]*>", re.IGNORECASE)
_HEAD_CLOSE = re.compile(r"</head>", re.IGNORECASE)
_BODY_CLOSE = re.compile(r"</body>", re.IGNORECASE)
# Pages locked to the viewport height cannot show a footer in normal flow.
_FIXED_LAYOUT = re.compile(r'class="(?:mapbody|atlasbar)\b')


def footer_html(compact: bool = False) -> str:
    classes = "fc-footer fc-footer-compact" if compact else "fc-footer"
    return (
        f'<footer class="{classes}" role="contentinfo">'
        '<div class="fc-footer-brand">'
        f'<img src="faerun-cartographers-96.png" alt="" width="48" height="48">'
        f"<div><strong>{html.escape(BRAND_NAME)}</strong><span>{html.escape(PRODUCT_NAME)}</span></div>"
        "</div>"
        '<div class="fc-footer-text">'
        f"<p>&copy; {COPYRIGHT_YEAR} {html.escape(BRAND_NAME)}. Published Realms maps and source "
        "material remain the property of their owners.</p>"
        f"<p>{TRADEMARK_NOTICE}</p>"
        "</div>"
        '<nav class="fc-footer-nav" aria-label="Footer">'
        '<a href="index.html">Markets</a><a href="location.html">Locations</a>'
        '<a href="map.html">Map</a>'
        "</nav>"
        "</footer>"
    )


def apply_branding(page: str) -> str:
    """Return an HTML page with the company logo, favicon and footer added."""
    if "fc-footer" in page:
        return page
    page = _TITLE.sub(
        lambda m: m[0] if BRAND_NAME in m[2] else f"{m[1]}{m[2]} | {BRAND_NAME}{m[3]}",
        page, count=1,
    )
    page = _HEAD_CLOSE.sub(lambda m: HEAD_LINKS + m[0], page, count=1)
    target = _BRAND_DIV.search(page) or _HEADER.search(page)
    if target is not None:
        page = page[:target.end()] + LOGO_LINK + page[target.end():]
    footer = footer_html(compact=bool(_FIXED_LAYOUT.search(page)))
    closing = list(_BODY_CLOSE.finditer(page))
    if closing:
        last = closing[-1]
        return page[:last.start()] + footer + page[last.start():]
    return page + footer

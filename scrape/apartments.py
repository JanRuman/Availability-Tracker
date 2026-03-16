from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from .http_client import HttpClient


@dataclass(frozen=True)
class ApartmentRef:
    id: str
    name: str
    url: str


LISTING_URL = "https://praga.at/apartmany/"


def _apartment_id_from_url(url: str) -> str:
    # Expected: /apartmany/<id>/<slug>/
    path = urlparse(url).path.strip("/")
    parts = path.split("/")
    if len(parts) >= 2 and parts[0] == "apartmany":
        return parts[1]
    return path.replace("/", "_")


def discover_apartments(client: HttpClient) -> list[ApartmentRef]:
    html = client.get_text(LISTING_URL)
    soup = BeautifulSoup(html, "html.parser")

    apartments: dict[str, ApartmentRef] = {}
    for a in soup.select('a[href^="https://praga.at/apartmany/"], a[href^="/apartmany/"]'):
        href = a.get("href")
        if not href:
            continue
        absolute = urljoin(LISTING_URL, href)
        parsed = urlparse(absolute)
        if parsed.netloc != "praga.at":
            continue

        # Keep only detail pages like /apartmany/<id>/<slug>/
        parts = parsed.path.strip("/").split("/")
        if len(parts) < 3 or parts[0] != "apartmany":
            continue
        if not parts[1].isdigit():
            continue

        # Avoid obvious non-detail pages (rare but safe)
        if parts[2] in {"apartmany", "apartments", "blog", "restaurant"}:
            continue

        apt_id = _apartment_id_from_url(absolute)
        name = " ".join(a.get_text(" ", strip=True).split())
        if not name:
            name = f"Apartment {apt_id}"

        apartments[absolute] = ApartmentRef(id=apt_id, name=name, url=absolute)

    # Stable ordering
    return sorted(apartments.values(), key=lambda x: (int(x.id) if x.id.isdigit() else 10**9, x.id))


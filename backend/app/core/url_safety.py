"""Guards for server-side HTTP fetches to reduce SSRF risk (Ollama probe, etc.)."""

from __future__ import annotations

import ipaddress
from urllib.parse import urlparse

_BLOCKLIST_HOSTS = frozenset(
    {
        "169.254.169.254",
        "metadata.google.internal",
        "metadata.goog",
    }
)


def assert_http_url_safe_for_fetch(url: str, *, allow_loopback: bool) -> str:
    """Validate scheme/host; optional block of loopback / RFC1918 / link-local targets.

    Raises ValueError with a short reason if the URL must not be fetched.
    """
    raw = (url or "").strip()
    if not raw:
        raise ValueError("URL is empty")

    parsed = urlparse(raw)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("Only http and https URLs are allowed")

    host = (parsed.hostname or "").strip().lower()
    if not host:
        raise ValueError("URL must include a hostname")

    if host in _BLOCKLIST_HOSTS:
        raise ValueError("Host is not allowed")

    if not allow_loopback:
        if host in ("localhost", "::1") or host.startswith("127."):
            raise ValueError("Loopback hosts are not allowed for this request")

        try:
            addr = ipaddress.ip_address(host)
            if addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_reserved:
                raise ValueError("Private, loopback, or reserved addresses are not allowed")
        except ValueError:
            # Not an IP literal — hostname allowed if not blocklisted.
            pass

    return raw

"""Shared Fish Audio endpoint validation without pipeline runtime imports."""

from __future__ import annotations

import ipaddress
from urllib.parse import urlparse


def validate_fish_audio_base_url(base_url: str) -> str:
    """Normalize a Fish Audio endpoint and reject unsafe clear-text URLs.

    Bearer credentials may be sent to HTTPS endpoints. Plain HTTP is accepted
    only for an explicit loopback host so the bundled local mock remains usable
    without allowing API keys to cross the network in clear text.
    """
    normalized = str(base_url or "").strip().rstrip("/")
    parsed = urlparse(normalized)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise RuntimeError("Fish Audio base_url must be an absolute HTTP(S) URL")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise RuntimeError(
            "Fish Audio base_url must not contain credentials, query, or fragment"
        )
    if parsed.scheme == "https":
        return normalized

    hostname = parsed.hostname.lower()
    is_loopback = hostname == "localhost"
    if not is_loopback:
        try:
            is_loopback = ipaddress.ip_address(hostname).is_loopback
        except ValueError:
            is_loopback = False
    if not is_loopback:
        raise RuntimeError(
            "Fish Audio base_url must use HTTPS; HTTP is allowed only for a loopback mock"
        )
    return normalized

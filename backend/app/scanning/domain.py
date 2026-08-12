import ipaddress
import re
from urllib.parse import urlparse

DOMAIN_PATTERN = re.compile(
    r"^(?=.{1,253}$)(?!-)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$"
)


def normalize_domain(value: str) -> str:
    candidate = value.strip().lower()

    if "://" in candidate:
        parsed = urlparse(candidate)
        candidate = parsed.hostname or ""
    else:
        candidate = candidate.split("/", 1)[0]

    candidate = candidate.strip(".")

    if not candidate:
        raise ValueError("Domain is required.")

    if _is_ip_address(candidate):
        raise ValueError("IP addresses are not allowed for snapshot checks.")

    if not DOMAIN_PATTERN.match(candidate):
        raise ValueError("Domain must be a valid hostname.")

    return candidate


def _is_ip_address(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
    except ValueError:
        return False

    return True

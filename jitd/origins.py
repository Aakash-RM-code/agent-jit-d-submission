"""Explicit origin policy for direct requests and an optional public reverse proxy."""
import os
from urllib.parse import urlsplit


def _host_port(value):
    u = urlsplit(value)
    if u.scheme not in ('http', 'https') or not u.hostname or u.username or u.password or u.path not in ('', '/') or u.query or u.fragment:
        return None
    return u.hostname, None if u.port in (None, 80, 443) else u.port


def _public_origin(value):
    u = urlsplit(value)
    if u.scheme != 'https' or not u.hostname or u.username or u.password or u.path not in ('', '/') or u.query or u.fragment:
        return None
    return u.scheme, u.hostname, u.port or 443


def mutation_origin_allowed(origin, base_url):
    if not origin:
        return True
    incoming = _host_port(origin)
    if incoming is None:
        return False
    if incoming == _host_port(base_url):
        return True
    try:
        configured = _public_origin(os.getenv('JITD_PUBLIC_ORIGIN', ''))
    except ValueError:
        configured = None
    return configured is not None and _public_origin(origin) == configured

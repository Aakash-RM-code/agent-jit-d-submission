"""Origin checks for a Vercel public URL forwarding to the Render app."""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize('origin,expected', [
    ('https://example-jitd.vercel.app', 405),
    ('https://example-jitd.vercel.app:443', 405),
    ('http://example-jitd.vercel.app', 403),
    ('https://example-jitd.vercel.app.evil.test', 403),
    ('https://unrelated.vercel.app', 403),
    ('null', 403),
])
def test_only_exact_configured_https_origin_passes(monkeypatch, origin, expected):
    monkeypatch.setenv('JITD_PROFILE', 'local')
    monkeypatch.setenv('JITD_REQUIRE_AUTH', '0')
    monkeypatch.delenv('JITD_ACCESS_TOKEN', raising=False)
    monkeypatch.setenv('JITD_PUBLIC_ORIGIN', 'https://example-jitd.vercel.app')
    from jitd.server import app
    with TestClient(app) as client:
        # Health supports GET only: 405 proves the origin gate passed, with no mutation.
        result = client.post('/api/health', headers={'Origin': origin})
        assert result.status_code == expected


def test_unconfigured_origin_and_spoofed_forwarded_host_refused(monkeypatch):
    monkeypatch.setenv('JITD_PROFILE', 'local')
    monkeypatch.setenv('JITD_REQUIRE_AUTH', '0')
    monkeypatch.delenv('JITD_ACCESS_TOKEN', raising=False)
    monkeypatch.delenv('JITD_PUBLIC_ORIGIN', raising=False)
    from jitd.server import app
    with TestClient(app) as client:
        result = client.post('/api/health', headers={'Origin': 'https://evil.test', 'X-Forwarded-Host': 'evil.test'})
        assert result.status_code == 403
        assert client.post('/api/health', headers={'Origin': 'http://testserver'}).status_code == 405

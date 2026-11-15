"""Adzuna fetch must survive a temporary 503 instead of failing the daily run."""
import httpx
import pytest

from pulse import adzuna


def _client(statuses):
    calls = {"n": 0}

    def handler(request):
        status = statuses[min(calls["n"], len(statuses) - 1)]
        calls["n"] += 1
        if status == 200:
            return httpx.Response(200, json={"results": []})
        return httpx.Response(status)

    return httpx.Client(transport=httpx.MockTransport(handler)), calls


def test_retries_after_temporary_503(monkeypatch):
    monkeypatch.setattr(adzuna.time, "sleep", lambda s: None)
    client, calls = _client([503, 503, 200])
    assert list(adzuna.fetch_role(client, "data engineer", 2, 1)) == []
    assert calls["n"] == 3


def test_gives_up_after_max_attempts(monkeypatch):
    monkeypatch.setattr(adzuna.time, "sleep", lambda s: None)
    client, calls = _client([503])
    with pytest.raises(httpx.HTTPStatusError):
        list(adzuna.fetch_role(client, "data engineer", 2, 1))
    assert calls["n"] == adzuna.MAX_ATTEMPTS


def test_does_not_retry_client_errors(monkeypatch):
    monkeypatch.setattr(adzuna.time, "sleep", lambda s: None)
    client, calls = _client([401])
    with pytest.raises(httpx.HTTPStatusError):
        list(adzuna.fetch_role(client, "data engineer", 2, 1))
    assert calls["n"] == 1

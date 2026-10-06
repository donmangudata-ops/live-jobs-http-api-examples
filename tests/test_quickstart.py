"""Offline tests for examples/quickstart.py.

No network and no Apify token are used. requests.post is replaced by a fake,
so the tests run for free and never start a paid request.
"""

import csv

import pytest

import quickstart


class FakeResponse:
    def __init__(self, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload if payload is not None else {}
        self.text = text

    def json(self):
        return self._payload


def sample_payload(**extra):
    payload = {
        "companies": [
            {"company": "stripe", "companyStatus": "ok"},
            {"company": "nope-inc", "companyStatus": "not_found"},
        ],
        "jobs": [
            {
                "company": "stripe",
                "ats": "greenhouse",
                "title": "Data Engineer",
                "location": "London",
                "url": "https://boards.greenhouse.io/stripe/jobs/1",
                "unexpectedField": "must be ignored",
            }
        ],
    }
    payload.update(extra)
    return payload


@pytest.fixture
def run_in_tmp(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_exits_without_token(run_in_tmp, monkeypatch):
    monkeypatch.delenv("APIFY_TOKEN", raising=False)
    monkeypatch.setattr(quickstart.sys, "argv", ["quickstart.py"])
    with pytest.raises(SystemExit) as exc:
        quickstart.main()
    assert "APIFY_TOKEN" in str(exc.value)


def test_posts_default_companies_with_bearer_token(run_in_tmp, monkeypatch):
    monkeypatch.setenv("APIFY_TOKEN", "test-token-not-real")
    monkeypatch.setattr(quickstart.sys, "argv", ["quickstart.py"])
    seen = {}

    def fake_post(url, json, headers, timeout):
        seen.update(url=url, json=json, headers=headers, timeout=timeout)
        return FakeResponse(payload=sample_payload())

    monkeypatch.setattr(quickstart.requests, "post", fake_post)
    quickstart.main()

    assert seen["url"] == quickstart.API_URL
    assert seen["json"]["companies"] == quickstart.DEFAULT_COMPANIES
    assert seen["json"]["postedSince"] == "30 days"
    assert seen["headers"]["Authorization"] == "Bearer test-token-not-real"
    assert seen["timeout"] >= 240


def test_uses_companies_from_arguments(run_in_tmp, monkeypatch):
    monkeypatch.setenv("APIFY_TOKEN", "test-token-not-real")
    monkeypatch.setattr(quickstart.sys, "argv", ["quickstart.py", "figma", "linear.app"])
    seen = {}

    def fake_post(url, json, headers, timeout):
        seen["companies"] = json["companies"]
        return FakeResponse(payload=sample_payload())

    monkeypatch.setattr(quickstart.requests, "post", fake_post)
    quickstart.main()
    assert seen["companies"] == ["figma", "linear.app"]


def test_writes_csv_and_ignores_unknown_fields(run_in_tmp, monkeypatch, capsys):
    monkeypatch.setenv("APIFY_TOKEN", "test-token-not-real")
    monkeypatch.setattr(quickstart.sys, "argv", ["quickstart.py"])
    monkeypatch.setattr(
        quickstart.requests, "post", lambda *a, **k: FakeResponse(payload=sample_payload())
    )
    quickstart.main()

    with open(run_in_tmp / "jobs.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 1
    assert rows[0]["title"] == "Data Engineer"
    assert "unexpectedField" not in rows[0]
    assert list(rows[0].keys()) == quickstart.COLUMNS

    out = capsys.readouterr().out
    assert "stripe: ok" in out
    assert "nope-inc: not_found" in out
    assert "Saved 1 jobs to jobs.csv" in out


def test_prints_spending_limit_notice(run_in_tmp, monkeypatch, capsys):
    monkeypatch.setenv("APIFY_TOKEN", "test-token-not-real")
    monkeypatch.setattr(quickstart.sys, "argv", ["quickstart.py"])
    monkeypatch.setattr(
        quickstart.requests,
        "post",
        lambda *a, **k: FakeResponse(payload=sample_payload(spendingLimitReached=True)),
    )
    quickstart.main()
    assert "spending limit" in capsys.readouterr().out


def test_exits_on_http_error(run_in_tmp, monkeypatch):
    monkeypatch.setenv("APIFY_TOKEN", "test-token-not-real")
    monkeypatch.setattr(quickstart.sys, "argv", ["quickstart.py"])
    monkeypatch.setattr(
        quickstart.requests,
        "post",
        lambda *a, **k: FakeResponse(status_code=401, text="unauthorized"),
    )
    with pytest.raises(SystemExit) as exc:
        quickstart.main()
    assert "HTTP 401" in str(exc.value)
    assert not (run_in_tmp / "jobs.csv").exists()

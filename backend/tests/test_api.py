from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)

GDPR = (
    "In the case of a personal data breach, the controller shall without undue delay "
    "and, where feasible, not later than 72 hours after having become aware of it, "
    "notify the personal data breach to the supervisory authority, unless the breach "
    "is unlikely to result in a risk to the rights and freedoms of natural persons."
)


def test_health_exposes_engine_version() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "regulatrace-api",
        "phase": "phase-1-deterministic",
        "engineVersion": "0.4.0-research",
    }


def test_openapi_documentation_exposes_all_phase_one_routes() -> None:
    docs_response = client.get("/api/docs")
    schema_response = client.get("/api/openapi.json")
    assert docs_response.status_code == 200
    assert schema_response.status_code == 200
    paths = schema_response.json()["paths"]
    assert {"/api/health", "/api/analyze", "/api/compare", "/api/versions/compare"}.issubset(paths)


def test_analyze_preserves_frontend_contract_and_metadata() -> None:
    response = client.post(
        "/api/analyze",
        json={
            "text": GDPR,
            "sourceMetadata": {
                "sourceId": "eur-lex://gdpr/33",
                "version": "2016-05-04",
                "authority": "European Union",
                "jurisdiction": "EU",
                "section": "Article 33",
            },
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["engineVersion"] == "0.4.0-research"
    assert payload["source"]["sourceId"] == "eur-lex://gdpr/33"
    assert payload["summary"]["citationIntegrity"] == 1
    assert payload["normative"][0]["modality"] == "OBLIGATION"
    assert "72 hours" in payload["normative"][0]["deadline"]
    assert "unlikely" in payload["normative"][0]["exception"]


def test_compare_flags_slower_policy_deadline() -> None:
    policy = "The controller shall notify the supervisory authority no later than 96 hours after confirming a reportable breach."
    response = client.post("/api/compare", json={"regulatoryText": GDPR, "policyText": policy})
    assert response.status_code == 200
    payload = response.json()
    assert payload["outcome"] == "POTENTIAL_MISMATCH"
    assert next(item for item in payload["dimensions"] if item["id"] == "timing")["score"] < 1


def test_version_compare_detects_modified_and_added_clauses() -> None:
    response = client.post(
        "/api/versions/compare",
        json={
            "oldText": "The organization shall review accounts every 90 days.",
            "newText": "The organization shall review accounts every 60 days. Dormant accounts must be disabled immediately.",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert any(change["type"] == "MODIFIED" for change in payload["changes"])
    assert any(change["type"] == "ADDED" for change in payload["changes"])
    assert payload["criticalCount"] >= 1


def test_whitespace_input_returns_structured_validation_error() -> None:
    response = client.post("/api/analyze", json={"text": "   ", "sourceMetadata": {}})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_local_frontend_origin_is_allowed_by_cors() -> None:
    response = client.options(
        "/api/analyze",
        headers={
            "Origin": "http://127.0.0.1:4173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:4173"


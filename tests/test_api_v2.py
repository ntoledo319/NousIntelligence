def test_api_v2_health(client):
    r = client.get("/api/v2/health")
    assert r.status_code == 200
    assert r.is_json
    assert r.get_json().get("ok") is True

def test_api_v2_monitoring_snapshot(client):
    r = client.get("/api/v2/monitoring/snapshot")
    assert r.status_code == 200
    data = r.get_json()
    assert data["ok"] is True
    snap = data["snapshot"]
    assert "cpu_percent" in snap and "mem_percent" in snap and "disk_percent" in snap

def test_api_v2_quality_score(client):
    r = client.post("/api/v2/quality/score", json={"text": "hello world this is a slightly longer test message"})
    assert r.status_code == 200
    data = r.get_json()
    assert data["ok"] is True
    assert "score" in data and "issues" in data

def test_api_v2_events_roundtrip(client):
    pub = client.post("/api/v2/events/publish", json={"topic": "test.topic", "payload": {"x": 1}})
    assert pub.status_code == 200
    recent = client.get("/api/v2/events/recent?prefix=test.&limit=10")
    assert recent.status_code == 200
    data = recent.get_json()
    assert data["ok"] is True
    assert isinstance(data["events"], list)

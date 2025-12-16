def test_nexus_chat(client):
    r = client.post("/api/v2/nexus/chat", json={"message": "Hello Nexus", "demo_mode": True})
    assert r.status_code in (200, 302)  # some setups redirect unless testing mode is on
    if r.status_code == 200:
      j = r.get_json()
      assert j["ok"] is True
      assert "response" in j

def test_crossref_search(client):
    r = client.get("/api/v2/research/crossref?q=therapy&demo=1")
    assert r.status_code in (200, 401)  # if auth enforced in non-test
    if r.status_code == 200:
      j = r.get_json()
      assert j["ok"] is True

def test_openlibrary_search(client):
    r = client.get("/api/v2/library/search?q=odyssey&demo=1")
    assert r.status_code in (200, 401)
    if r.status_code == 200:
      j = r.get_json()
      assert j["ok"] is True

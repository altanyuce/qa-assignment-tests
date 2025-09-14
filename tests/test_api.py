import uuid
import requests

BASE_URL = "http://localhost:8000"

def make_user(username=None, email=None, age=25, password="Passw0rd!"):
    if username is None:
        username = f"u_{uuid.uuid4().hex[:8]}"
    if email is None:
        email = f"{username}@example.com"
    return {"username": username, "email": email, "password": password, "age": age}

def login(username, password):
    r = requests.post(f"{BASE_URL}/login", json={"username": username, "password": password})
    assert r.status_code == 200, f"login failed: {r.text}"
    return r.json()["token"]

def test_root_ok():
    r = requests.get(f"{BASE_URL}/")
    assert r.status_code == 200
    j = r.json()
    assert j.get("message") == "User Management API"
    assert j.get("version") == "1.0.0"

def test_create_user_ok_and_lowercase_username():
    payload = make_user(username="Altan_Tmp")
    r = requests.post(f"{BASE_URL}/users", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert body["username"] == payload["username"].lower()
    assert body["email"] == payload["email"]
    assert body["is_active"] is True

def test_create_user_duplicate_should_fail():
    payload = make_user(username="dup_user")
    r1 = requests.post(f"{BASE_URL}/users", json=payload)
    r2 = requests.post(f"{BASE_URL}/users", json=payload)
    assert r2.status_code == 400  # Username already exists

def test_get_user_and_list_pagination():

    r1 = requests.post(f"{BASE_URL}/users", json=make_user())
    r2 = requests.post(f"{BASE_URL}/users", json=make_user())
    id1 = r1.json()["id"]

    g = requests.get(f"{BASE_URL}/users/{id1}")
    assert g.status_code == 200
    assert g.json()["id"] == id1

    l = requests.get(f"{BASE_URL}/users", params={"limit": 1, "offset": 0})
    assert l.status_code == 200
    assert len(l.json()) == 1

def test_login_seed_user_ok():
    r = requests.post(f"{BASE_URL}/login", json={"username": "john_doe", "password": "password123"})
    assert r.status_code == 200 and "token" in r.json()

def test_put_requires_bearer_token():
    r = requests.put(f"{BASE_URL}/users/1", json={"email": "x@y.com"})
    assert r.status_code == 401  # Should require Authorization header (expect 401)

def test_cross_user_update_authorization_bug():

    import time
    u1 = make_user(username="u1_"+uuid.uuid4().hex[:6])
    u2 = make_user(username="u2_"+uuid.uuid4().hex[:6])
    r1 = requests.post(f"{BASE_URL}/users", json=u1)
    r2 = requests.post(f"{BASE_URL}/users", json=u2)
    id2 = r2.json()["id"]

    token = login(u1["username"], u1["password"])

    new_mail = f"takeover_{uuid.uuid4().hex[:6]}@ex.com"
    upd = requests.put(f"{BASE_URL}/users/{id2}",
                       headers={"Authorization": f"Bearer {token}"},
                       json={"email": new_mail})

    assert upd.status_code == 200
    assert upd.json()["email"] == new_mail

def test_delete_with_basic_auth_weak_authorization_bug():
    victim = make_user(username="victim_"+uuid.uuid4().hex[:6])
    rv = requests.post(f"{BASE_URL}/users", json=victim)
    victim_id = rv.json()["id"]

    r = requests.delete(f"{BASE_URL}/users/{victim_id}", auth=("john_doe", "password123"))

    assert r.status_code == 200

def test_stats_info_leak_bug():
    r = requests.get(f"{BASE_URL}/stats", params={"include_details": "true"})
    assert r.status_code == 200
    body = r.json()
    assert "user_emails" in body and "session_tokens" in body

def test_search_username_and_email():
    u = make_user(username="search_me", email="search_me@example.com")
    requests.post(f"{BASE_URL}/users", json=u)

    r1 = requests.get(f"{BASE_URL}/users/search", params={"q": "search", "field": "username"})

    assert r1.status_code in (200, 400)

    r2 = requests.get(f"{BASE_URL}/users/search", params={"q": "search_me", "field": "all"})
    assert r2.status_code == 200
    assert any(x["username"] == "search_me" for x in r2.json())

def test_health_ok():
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200
    assert r.json().get("status") == "healthy"

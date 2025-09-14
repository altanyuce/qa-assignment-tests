# bugs_report.md

## Executive Summary
This report documents the defects identified in the **User Management API** through manual exploratory testing and automated pytest scripts.  
The issues mainly concern **authorization, security, validation, and pagination**.  
As required in **QA_ASSIGNMENT.md**, at least 10 bugs have been documented.  

---

## BUG-001: Pagination off-by-one (limit+1 records returned)
**Severity:** Medium  
**Category:** Logic / Pagination  

**Description:** The `GET /users` endpoint returns 2 records when `limit=1`. The slicing logic behaves as `offset : offset + limit + 1`.  

**Steps to Reproduce:**
1. Create at least two users (via seed or `POST /users`).  
2. Call `GET /users?limit=1&offset=0`.  

**Expected Result:** Exactly 1 record should be returned.  
**Actual Result:** 2 records are returned.  

**Evidence:**
```bash
curl "http://localhost:8000/users?limit=1&offset=0"
# => 2 records
```

---

## BUG-002: Search (field=username) returns 400 Bad Request
**Severity:** Medium/High  
**Category:** Validation / API Behavior  

**Description:** A valid call `/users/search?q=search&field=username` incorrectly returns 400.  

**Steps to Reproduce:**
1. Create a user with `username="search_me"`.  
2. Call `GET /users/search?q=search&field=username`.  

**Expected Result:** 200 with matching users.  
**Actual Result:** 400 Bad Request.  

**Evidence:**
```bash
curl "http://localhost:8000/users/search?q=search&field=username"
# => 400
```

---

## BUG-003: Unauthorized user can update another user’s profile (PUT)
**Severity:** High  
**Category:** Authorization  

**Description:** No owner/role validation in `PUT /users/{id}`. User A can update User B’s profile.  

**Steps to Reproduce:**
1. Create users A and B.  
2. Login as A, obtain a token.  
3. Send `PUT /users/{B_id}` with A’s token.  

**Expected Result:** 403/401 Forbidden.  
**Actual Result:** 200 OK and B’s data updated.  

**Evidence:**
```bash
curl -X PUT "http://localhost:8000/users/2"  -H "Authorization: Bearer <token_of_user_A>"  -H "Content-Type: application/json"  -d '{"email":"takeover@ex.com"}'
# => 200
```

---

## BUG-004: Deletion with Basic Auth ignores role/ownership
**Severity:** High  
**Category:** Authorization  

**Description:** `DELETE /users/{id}` accepts Basic Auth; any valid user can deactivate another account.  

**Steps to Reproduce:**
1. Create a victim user.  
2. Another user (e.g., seed `john_doe`) sends a DELETE request with Basic Auth.  

**Expected Result:** 403/401 or restricted to owner/admin only.  
**Actual Result:** 200 OK, victim user is deactivated.  

**Evidence:**
```bash
curl -X DELETE "http://localhost:8000/users/<victim_id>"  -u john_doe:password123
# => 200
```

---

## BUG-005: Sensitive information disclosure via `/stats?include_details=true`
**Severity:** Critical  
**Category:** Security / Information Disclosure  

**Description:** `/stats?include_details=true` exposes user emails and session tokens.  

**Steps to Reproduce:**
1. Call `GET /stats?include_details=true`.  

**Expected Result:** Sensitive data not exposed, or accessible to admins only.  
**Actual Result:** `user_emails` and `session_tokens` are included in response.  

**Evidence:**
```bash
curl "http://localhost:8000/stats?include_details=true"
# => { "user_emails":[...], "session_tokens":[...] }
```

---

## BUG-006: Session expiry check disabled
**Severity:** High  
**Category:** Security / Session Management  

**Description:** The session expiration check in `verify_session` is commented out. Tokens never expire.  

**Steps to Reproduce:**
1. Log in and obtain a session token.  
2. Wait longer than the supposed expiration period.  
3. Call any authenticated endpoint with the same token.  

**Expected Result:** API should return 401 Unauthorized.  
**Actual Result:** Token still works.  

**Evidence:**
```python
def verify_session(token: str):
    if token not in sessions:
        return None
    session = sessions[token]
    # if datetime.utcnow() > session["expires_at"]:   <-- commented out
    #     return None
    return session
```

---

## BUG-007: Weak password hashing (MD5 + fixed salt)
**Severity:** High  
**Category:** Security / Cryptography  

**Description:** Passwords are hashed with `hashlib.md5` and a fixed salt. This is outdated and insecure.  

**Steps to Reproduce:**
1. Inspect the `hash_password` function in the code.  
2. Observe that MD5 with a static salt is used.  
3. Try hashing `password123` and match with rainbow tables.  

**Expected Result:** Strong hashing like `bcrypt` or `argon2`.  
**Actual Result:** MD5 with fixed salt.  

**Evidence:**
```python
def hash_password(password: str):
    salt = "static_salt"
    return hashlib.md5((password + salt).encode()).hexdigest()
```

---

## BUG-008: Risky username validation (quotes, semicolon allowed)
**Severity:** Medium  
**Category:** Validation / Security  

**Description:** Username regex allows unsafe characters (`' " ;`).  

**Steps to Reproduce:**
1. Create a user with `username="bad'user;--"`.  
2. Observe that the request is accepted.  

**Expected Result:** API should reject unsafe characters.  
**Actual Result:** User is created successfully.  

**Evidence:**
```bash
curl -X POST http://localhost:8000/users  -H "Content-Type: application/json"  -d '{"username": "bad";--", "email": "x@y.com", "password": "Passw0rd!", "age": 25}'
# => 201 Created
```

---

## BUG-009: Race condition risk in concurrent access
**Severity:** Medium/High  
**Category:** Concurrency / Data Integrity  

**Description:** Global dictionaries (`users_db`, `sessions`) are updated without locks.  

**Steps to Reproduce:**
1. Run multiple parallel requests creating/updating users.  
2. Observe inconsistent states or errors.  

**Expected Result:** Thread-safe handling.  
**Actual Result:** Possible inconsistency.  

**Evidence:**
```python
# users_db is updated directly with no locking
users_db[user_id] = user
```

---

## BUG-010: Rate limiting weakness / spoofable IP
**Severity:** Medium  
**Category:** Security / Abuse Prevention  

**Description:** Rate limiting relies on IP and trusts `X-Forwarded-For`, which can be spoofed.  

**Steps to Reproduce:**
1. Send multiple requests with different `X-Forwarded-For` headers.  
2. Observe that rate limit is bypassed.  

**Expected Result:** Requests should be blocked after the limit.  
**Actual Result:** All succeed.  

**Evidence:**
```bash
for i in {1..50}; do
  curl -H "X-Forwarded-For: 123.123.123.$i" http://localhost:8000/health
done
# => All succeed
```

---

## BUG-011 (Bonus): `created_at` sorted as string
**Severity:** Low/Medium  
**Category:** Sorting / Consistency  

**Description:** `created_at` is stored as a string and sorted incorrectly.  

**Steps to Reproduce:**
1. Create users at different times.  
2. List users sorted by `created_at`.  

**Expected Result:** Sorted by datetime values.  
**Actual Result:** Sorted by strings.  

**Evidence:**
```python
users_list.sort(key=lambda u: u["created_at"])
# created_at is string, not datetime
```

---

## BUG-012 (Bonus): `POST /users/bulk` accessible without authentication
**Severity:** High  
**Category:** Security / Access Control  

**Description:** `/users/bulk` is accessible without authentication, despite `include_in_schema=False`.  

**Steps to Reproduce:**
1. Call `POST /users/bulk` without credentials.  
2. Observe that users are created.  

**Expected Result:** 401/403 Unauthorized.  
**Actual Result:** Bulk creation succeeds.  

**Evidence:**
```bash
curl -X POST http://localhost:8000/users/bulk  -H "Content-Type: application/json"  -d '[{"username": "a1", "email": "a1@ex.com", "password": "p", "age": 20}]'
# => 201 Created
```

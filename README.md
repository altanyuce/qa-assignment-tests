# User Management API - QA Testing Project  

## About this Project  
This repository was created as part of a **QA case study** for a User Management API.  
The main goal was to evaluate the system’s **functionality, security, and validation** through:  
- **Manual exploratory testing**  
- **Automated API testing** using `pytest`  
- **Bug reporting and documentation** in Markdown/PDF  

---

## Objectives  
- Validate **core user flows**: create, read, update, delete (CRUD).  
- Assess **authentication and session management**.  
- Check **input validation and search behavior**.  
- Identify **security vulnerabilities** (authorization flaws, weak password hashing, info leaks).  

---

## Tools & Technologies  
- **Python 3.12**  
- **Pytest** for test automation  
- **Requests library** for API interaction  
- **cURL / Postman** for manual testing  
- Documentation in **Markdown & PDF**  

---

## Test Results  
- **Total automated test cases:** 11  
- **Passed / Failed:** 9 / 2  
- **Bugs discovered:** 10+  
- **Severity distribution:**  
  - Critical: 1  
  - High: 3–4  
  - Medium: 3–4  
  - Low: 1–2  

---

## Key Findings (Sample)  
- **Pagination bug:** `GET /users?limit=1` returned 2 records.  
- **Authorization flaw:** Any user could update/delete another user’s profile.  
- **Sensitive info disclosure:** `/stats?include_details=true` exposed emails & session tokens.  
- **Weak password hashing:** MD5 with static salt.  
- **No session expiration:** Tokens never expire.  

Full list available in [`bugs_report.md`](./bugs_report.md).  

---

## 📑 Deliverables  
- [`bugs_report.md`](./bugs_report.md) – Detailed bug descriptions, reproduction steps, and evidence.  
- [`test_report.md`](./test_report.md) – Executive summary, metrics, recommendations, and security assessment.  
- [`tests/test_api.py`](./tests/test_api.py) – Automated pytest suite.  

---

# How to Run

## Prerequisites
- Python 3.10+
- **Application dependencies (in the app repository):**
  ```bash
  pip install -r requirements.txt
  ```
- **Test dependencies (in this test repository):**
  ```bash
  pip install -r requirements_test.txt
  ```
  
---

## Start the API
Run the application locally **in a separate terminal** (from the app repository):

Linux / macOS:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Windows (alternative):
```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Important:** Keep this terminal running. The tests assume the API is already running at `http://localhost:8000`.

---

## (Optional) Load Seed Data
```bash
python seed_data.py
```

---

## Run the Tests
From this test repository, you can run the tests either using a pytest run configuration in PyCharm or directly from the terminal:
```bash
pytest -q
```

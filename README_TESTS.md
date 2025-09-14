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

⚠️ **Important:** Keep this terminal running. The tests assume the API is already running at `http://localhost:8000`.

## (Optional) Load Seed Data
```bash
python seed_data.py
```

## Run the Tests
From this test repository, you can run the tests either using a pytest run configuration in PyCharm or directly from the terminal:
```bash
pytest -q
```

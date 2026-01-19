Run locally

1. Create venv and activate it
python -m venv .venv
.\.venv\Scripts\Activate.ps1

2. Install dependencies
pip install -r requirements.txt

3. Create a .env file based on .env.example

4. Run
python run_local.py

Open http://127.0.0.1:5000

Deploy to App Engine

1. Ensure app.yaml exists at repo root
2. gcloud app deploy
3. Test /api/health on the deployed URL

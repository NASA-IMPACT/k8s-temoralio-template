
uv run uvicorn fastapi_run:app --host 0.0.0.0 --port 8000 &

API_PID=$!
trap "echo 'Stopping FastAPI...'; kill -TERM $API_PID; wait $API_PID; exit 0" INT TERM

uv run main.py

#uv run uvicorn fastapi_run:app --host 0.0.0.0 --port 8000

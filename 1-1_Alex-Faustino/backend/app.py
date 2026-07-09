from fastapi import FastAPI

from schemas import Customer
from services.predictor import ChurnPredictor
from services.ai_agent import AIAgent
from services.validators import validate_customer
from services import metrics
from services import persistence
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request, Header, HTTPException
import os
import jwt
import datetime
from typing import Optional

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")

import logging

templates = Jinja2Templates(directory="templates")

logging.basicConfig(
    level=logging.INFO,
    filename="api.log",
    format="%(asctime)s %(message)s"
)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

predictor = ChurnPredictor()
agent = AIAgent()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    import time

    start = time.time()
    response = await call_next(request)
    duration = time.time() - start

    # record latency per path
    path = request.url.path
    try:
        metrics.record_latency(path, duration)
    except Exception:
        pass

    # attach header for debugging
    response.headers["X-Process-Time"] = str(round(duration, 4))
    return response

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/")
def home(request: Request):
    # render the frontend; the frontend will handle login and request the API key
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )
    
@app.post("/predict")
def predict(customer: Customer, x_api_key: str | None = Header(None)):

    # API key protection: if PREDICT_API_KEY is set, require matching header
    expected = os.getenv("PREDICT_API_KEY")
    if expected:
        if not x_api_key or x_api_key != expected:
            raise HTTPException(status_code=401, detail="Unauthorized")

    customer_data = customer.model_dump()
    
    validate_customer(customer_data)

    prediction = predictor.predict(customer_data)

    # record that a prediction happened
    try:
        metrics.increment_counter("predictions")
    except Exception:
        pass
    

    explanation = agent.explain(
        customer_data,
        prediction
    )
    
    logging.info(
        f"Probabilidade: {prediction['probabilidade']}"
    )

    return {
        **prediction,
        **explanation
    }



@app.post("/login")
def login(credentials: dict):
    """Simple login endpoint that returns a signed JWT when credentials match env vars."""

    username = credentials.get("username")
    password = credentials.get("password")

    expected_user = os.getenv("FRONTEND_USER")
    expected_pass = os.getenv("FRONTEND_PASSWORD")

    if not expected_user or not expected_pass:
        raise HTTPException(status_code=500, detail="Frontend credentials not configured on server")

    if username != expected_user or password != expected_pass:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    payload = {
        "sub": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=4)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return {"access_token": token, "token_type": "bearer"}


@app.get("/get_api_key")
def get_api_key(authorization: Optional[str] = Header(None)):
    """Return the configured `PREDICT_API_KEY` to authenticated frontend clients.

    The frontend must call `/login` to obtain a Bearer token and then call this
    endpoint with header `Authorization: Bearer <token>`.
    """

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = authorization.split(" ", 1)[1]

    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    # token valid; return API key
    key = os.getenv("PREDICT_API_KEY")
    if not key:
        raise HTTPException(status_code=500, detail="PREDICT_API_KEY not configured on server")

    return {"api_key": key}


@app.get("/metrics")
def metrics_endpoint():
    """Retorna métricas de observabilidade do serviço."""
    return metrics.get_metrics()



@app.on_event("startup")
def _start_background_tasks():
    # start persistence worker to save metrics periodically
    try:
        persistence.start_persistence()
    except Exception:
        pass


@app.on_event("shutdown")
def _stop_background_tasks():
    try:
        persistence.stop_persistence()
    except Exception:
        pass
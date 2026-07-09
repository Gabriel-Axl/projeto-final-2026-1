from fastapi import FastAPI

from schemas import Customer
from services.predictor import ChurnPredictor
from services.ai_agent import AIAgent
from services.validators import validate_customer
from services import metrics
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request

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
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={}
    )
    
@app.post("/predict")
def predict(customer: Customer):

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


@app.get("/metrics")
def metrics_endpoint():
    """Retorna métricas de observabilidade do serviço."""
    return metrics.get_metrics()
from fastapi import FastAPI

from schemas import Customer
from services.predictor import ChurnPredictor
from services.ai_agent import AIAgent
from services.validators import validate_customer
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
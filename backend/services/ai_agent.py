import json
import logging
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.1-flash")


class AIAgent:

    def explain(self, customer, prediction):

        prompt = f"""
Você é um especialista em retenção de clientes.

Analise os dados abaixo.

Dados do cliente:
{customer}

Resultado do modelo:
{prediction}

Responda SOMENTE em JSON no formato:

{{
    "explicacao":"...",
    "acao_sugerida":"..."
}}
"""

        try:

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    response_mime_type="application/json"
                )
            )

            return json.loads(
                response.text
            )

        except Exception as e:

            print(f"Erro ao chamar Gemini: {e}")
            logging.error(e)
            
            return {
                "explicacao": "Não foi possível gerar uma explicação automática.",
                "acao_sugerida": "Realizar análise manual do cliente."
            }
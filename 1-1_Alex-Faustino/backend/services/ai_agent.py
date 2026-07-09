import json
import logging
import os
import re
from typing import Any, Dict

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, ValidationError

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.1-flash")


class AgentResponse(BaseModel):
    explicacao: str
    acao_sugerida: str


def _sanitize_text(s: str) -> str:
    # remove HTML tags and control characters, limit length
    if not isinstance(s, str):
        s = str(s)
    # strip HTML tags
    s = re.sub(r"<[^>]*>", "", s)
    # remove non-printable
    s = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", s)
    # collapse whitespace
    s = re.sub(r"\s+", " ", s).strip()
    # limit length
    return s[:4000]


class AIAgent:

    def explain(self, customer: Dict[str, Any], prediction: Dict[str, Any]) -> Dict[str, str]:

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

            # parse JSON
            raw = json.loads(response.text)

            # record that we called LLM and estimate cost
            try:
                # increment llm call counter
                from services import metrics as _metrics

                _metrics.increment_counter("llm_calls")
                # estimate cost per call (env var optional)
                cost_per_call = float(os.getenv("GEMINI_COST_PER_CALL", "0.0"))
                if cost_per_call > 0:
                    _metrics.add_cost(cost_per_call)
            except Exception:
                pass

            # validate schema
            try:
                parsed = AgentResponse.model_validate(raw)

                # sanitize fields
                return {
                    "explicacao": _sanitize_text(parsed.explicacao),
                    "acao_sugerida": _sanitize_text(parsed.acao_sugerida),
                }

            except ValidationError as ve:
                logging.warning(f"Agent response failed schema validation: {ve}")
                logging.debug(f"Raw agent response: %s", raw)
                # increment fallback counter
                try:
                    from services import metrics as _metrics

                    _metrics.increment_counter("llm_fallbacks")
                except Exception:
                    pass
                raise

        except Exception as e:

            logging.error("Erro ao gerar/validar resposta do agente: %s", e)

            # increment fallback counter
            try:
                from services import metrics as _metrics

                _metrics.increment_counter("llm_fallbacks")
            except Exception:
                pass

            return {
                "explicacao": "Não foi possível gerar uma explicação automática.",
                "acao_sugerida": "Realizar análise manual do cliente."
            }
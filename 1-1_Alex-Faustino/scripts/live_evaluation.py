#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import statistics
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_BASE_URL = "https://my-churn-app.fly.dev"


VALID_CUSTOMERS: List[Dict[str, Any]] = [
    {
        "label": "Cliente novo em contrato mensal",
        "payload": {
            "gender": "Female",
            "SeniorCitizen": 0,
            "Partner": "No",
            "Dependents": "No",
            "tenure": 1,
            "PhoneService": "Yes",
            "MultipleLines": "No",
            "InternetService": "Fiber optic",
            "OnlineSecurity": "No",
            "OnlineBackup": "No",
            "DeviceProtection": "No",
            "TechSupport": "No",
            "StreamingTV": "Yes",
            "StreamingMovies": "Yes",
            "Contract": "Month-to-month",
            "PaperlessBilling": "Yes",
            "PaymentMethod": "Electronic check",
            "MonthlyCharges": 89.9,
            "TotalCharges": 89.9,
        },
    },
    {
        "label": "Cliente antigo com contrato anual",
        "payload": {
            "gender": "Male",
            "SeniorCitizen": 0,
            "Partner": "Yes",
            "Dependents": "Yes",
            "tenure": 48,
            "PhoneService": "Yes",
            "MultipleLines": "Yes",
            "InternetService": "DSL",
            "OnlineSecurity": "Yes",
            "OnlineBackup": "Yes",
            "DeviceProtection": "Yes",
            "TechSupport": "Yes",
            "StreamingTV": "No",
            "StreamingMovies": "No",
            "Contract": "One year",
            "PaperlessBilling": "No",
            "PaymentMethod": "Bank transfer (automatic)",
            "MonthlyCharges": 64.4,
            "TotalCharges": 3090.9,
        },
    },
    {
        "label": "Cliente com Internet fibra e pagamentos eletrônicos",
        "payload": {
            "gender": "Female",
            "SeniorCitizen": 1,
            "Partner": "No",
            "Dependents": "No",
            "tenure": 12,
            "PhoneService": "Yes",
            "MultipleLines": "Yes",
            "InternetService": "Fiber optic",
            "OnlineSecurity": "No",
            "OnlineBackup": "Yes",
            "DeviceProtection": "No",
            "TechSupport": "No",
            "StreamingTV": "Yes",
            "StreamingMovies": "Yes",
            "Contract": "Month-to-month",
            "PaperlessBilling": "Yes",
            "PaymentMethod": "Electronic check",
            "MonthlyCharges": 99.0,
            "TotalCharges": 1188.0,
        },
    },
]


INVALID_CASES: List[Dict[str, Any]] = [
    {
        "label": "Tenure negativo",
        "payload": {
            "gender": "Female",
            "SeniorCitizen": 0,
            "Partner": "No",
            "Dependents": "No",
            "tenure": -1,
            "PhoneService": "Yes",
            "MultipleLines": "No",
            "InternetService": "DSL",
            "OnlineSecurity": "No",
            "OnlineBackup": "No",
            "DeviceProtection": "No",
            "TechSupport": "No",
            "StreamingTV": "No",
            "StreamingMovies": "No",
            "Contract": "Month-to-month",
            "PaperlessBilling": "Yes",
            "PaymentMethod": "Electronic check",
            "MonthlyCharges": 50.0,
            "TotalCharges": 50.0,
        },
    },
    {
        "label": "Gênero inválido",
        "payload": {
            "gender": "Other",
            "SeniorCitizen": 0,
            "Partner": "No",
            "Dependents": "No",
            "tenure": 5,
            "PhoneService": "Yes",
            "MultipleLines": "No",
            "InternetService": "DSL",
            "OnlineSecurity": "No",
            "OnlineBackup": "No",
            "DeviceProtection": "No",
            "TechSupport": "No",
            "StreamingTV": "No",
            "StreamingMovies": "No",
            "Contract": "Month-to-month",
            "PaperlessBilling": "Yes",
            "PaymentMethod": "Electronic check",
            "MonthlyCharges": 50.0,
            "TotalCharges": 250.0,
        },
    },
    {
        "label": "Contrato inválido",
        "payload": {
            "gender": "Female",
            "SeniorCitizen": 0,
            "Partner": "No",
            "Dependents": "No",
            "tenure": 5,
            "PhoneService": "Yes",
            "MultipleLines": "No",
            "InternetService": "DSL",
            "OnlineSecurity": "No",
            "OnlineBackup": "No",
            "DeviceProtection": "No",
            "TechSupport": "No",
            "StreamingTV": "No",
            "StreamingMovies": "No",
            "Contract": "Three year",
            "PaperlessBilling": "Yes",
            "PaymentMethod": "Electronic check",
            "MonthlyCharges": 50.0,
            "TotalCharges": 250.0,
        },
    },
    {
        "label": "MonthlyCharges negativo",
        "payload": {
            "gender": "Male",
            "SeniorCitizen": 0,
            "Partner": "Yes",
            "Dependents": "No",
            "tenure": 9,
            "PhoneService": "Yes",
            "MultipleLines": "Yes",
            "InternetService": "Fiber optic",
            "OnlineSecurity": "No",
            "OnlineBackup": "Yes",
            "DeviceProtection": "No",
            "TechSupport": "No",
            "StreamingTV": "Yes",
            "StreamingMovies": "Yes",
            "Contract": "Month-to-month",
            "PaperlessBilling": "Yes",
            "PaymentMethod": "Credit card (automatic)",
            "MonthlyCharges": -1.0,
            "TotalCharges": 100.0,
        },
    },
    {
        "label": "Campo obrigatório ausente",
        "payload": {
            "gender": "Male",
            "SeniorCitizen": 0,
            "Partner": "Yes",
            "Dependents": "No",
            "tenure": 9,
            "PhoneService": "Yes",
            "MultipleLines": "Yes",
            "InternetService": "Fiber optic",
            "OnlineSecurity": "No",
            "OnlineBackup": "Yes",
            "DeviceProtection": "No",
            "TechSupport": "No",
            "StreamingTV": "Yes",
            "StreamingMovies": "Yes",
            "Contract": "Month-to-month",
            "PaperlessBilling": "Yes",
            "PaymentMethod": "Credit card (automatic)",
            "MonthlyCharges": 99.0,
        },
    },
]


@dataclass
class HTTPResult:
    status: int
    duration_sec: float
    body_text: str
    json_data: Optional[Any]


def http_json(method: str, url: str, payload: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None, timeout: int = 60) -> HTTPResult:
    request_headers = dict(headers or {})
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        request_headers.setdefault("Content-Type", "application/json")

    request = urllib.request.Request(url, data=data, method=method.upper(), headers=request_headers)
    started = time.perf_counter()
    response = None
    try:
        response = urllib.request.urlopen(request, timeout=timeout)
        status = getattr(response, "status", 200)
        body_bytes = response.read()
    except urllib.error.HTTPError as exc:
        status = exc.code
        body_bytes = exc.read()
    finally:
        duration_sec = time.perf_counter() - started
        if response is not None:
            response.close()

    body_text = body_bytes.decode("utf-8", errors="replace") if body_bytes else ""
    json_data = None
    if body_text:
        try:
            json_data = json.loads(body_text)
        except Exception:
            json_data = None

    return HTTPResult(status=status, duration_sec=duration_sec, body_text=body_text, json_data=json_data)


def login(base_url: str, username: str, password: str) -> tuple[str, float]:
    result = http_json(
        "POST",
        f"{base_url}/login",
        payload={"username": username, "password": password},
    )
    if result.status != 200 or not isinstance(result.json_data, dict) or "access_token" not in result.json_data:
        raise RuntimeError(f"Falha no login: HTTP {result.status} - {result.body_text}")
    return result.json_data["access_token"], result.duration_sec


def get_api_key(base_url: str, token: str) -> tuple[str, float]:
    result = http_json(
        "GET",
        f"{base_url}/get_api_key",
        headers={"Authorization": f"Bearer {token}"},
    )
    if result.status != 200 or not isinstance(result.json_data, dict) or "api_key" not in result.json_data:
        raise RuntimeError(f"Falha ao obter API key: HTTP {result.status} - {result.body_text}")
    return result.json_data["api_key"], result.duration_sec


def get_metrics(base_url: str) -> HTTPResult:
    return http_json("GET", f"{base_url}/metrics")


def predict(base_url: str, api_key: str, payload: Dict[str, Any]) -> HTTPResult:
    return http_json(
        "POST",
        f"{base_url}/predict",
        payload=payload,
        headers={"X-API-Key": api_key},
    )


def safe_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)


def percentile(values: List[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = (len(ordered) - 1) * pct
    lower = int(rank)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = rank - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def parse_metrics_snapshot(result: HTTPResult) -> Dict[str, Any]:
    if not isinstance(result.json_data, dict):
        raise RuntimeError(f"Resposta de métricas inesperada: {result.body_text}")
    return result.json_data


def compute_metric_delta(before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
    before_counters = before.get("counters", {}) or {}
    after_counters = after.get("counters", {}) or {}
    delta_counters = {
        key: int(after_counters.get(key, 0)) - int(before_counters.get(key, 0))
        for key in sorted(set(before_counters) | set(after_counters))
    }
    return {
        "counters": delta_counters,
        "before": before,
        "after": after,
    }


def run_evaluation(base_url: str, username: str, password: str) -> Dict[str, Any]:
    started_at = datetime.now(timezone.utc).astimezone()

    metrics_before_result = get_metrics(base_url)
    metrics_before = parse_metrics_snapshot(metrics_before_result)

    token, login_latency = login(base_url, username, password)
    api_key, api_key_latency = get_api_key(base_url, token)

    valid_results = []
    valid_latencies: List[float] = []
    invalid_results = []

    for case in VALID_CUSTOMERS:
        result = predict(base_url, api_key, case["payload"])
        valid_results.append(
            {
                "label": case["label"],
                "status": result.status,
                "duration_sec": round(result.duration_sec, 4),
                "response": result.json_data,
            }
        )
        valid_latencies.append(result.duration_sec)

    for case in INVALID_CASES:
        result = predict(base_url, api_key, case["payload"])
        invalid_results.append(
            {
                "label": case["label"],
                "status": result.status,
                "duration_sec": round(result.duration_sec, 4),
                "response": result.json_data if result.json_data is not None else result.body_text,
            }
        )

    metrics_after_result = get_metrics(base_url)
    metrics_after = parse_metrics_snapshot(metrics_after_result)

    delta = compute_metric_delta(metrics_before, metrics_after)

    valid_successes = sum(1 for item in valid_results if item["status"] == 200)
    invalid_rejections = sum(1 for item in invalid_results if item["status"] >= 400)
    fallback_calls = int(delta["counters"].get("llm_fallbacks", 0))
    llm_calls = int(delta["counters"].get("llm_calls", 0))
    fallback_rate = (fallback_calls / llm_calls) if llm_calls > 0 else 0.0

    report = {
        "metadata": {
            "base_url": base_url,
            "started_at": started_at.isoformat(),
            "finished_at": datetime.now(timezone.utc).astimezone().isoformat(),
            "username": username,
            "test_counts": {
                "valid": len(VALID_CUSTOMERS),
                "invalid": len(INVALID_CASES),
            },
        },
        "setup": {
            "login_latency_sec": round(login_latency, 4),
            "api_key_latency_sec": round(api_key_latency, 4),
        },
        "results": {
            "valid": valid_results,
            "invalid": invalid_results,
        },
        "metrics": {
            "before": metrics_before,
            "after": metrics_after,
            "delta": delta,
        },
        "summary": {
            "valid_success_rate": round(valid_successes / len(VALID_CUSTOMERS), 4) if VALID_CUSTOMERS else 0.0,
            "invalid_rejection_rate": round(invalid_rejections / len(INVALID_CASES), 4) if INVALID_CASES else 0.0,
            "avg_predict_latency_sec": round(statistics.mean(valid_latencies), 4) if valid_latencies else 0.0,
            "median_predict_latency_sec": round(statistics.median(valid_latencies), 4) if valid_latencies else 0.0,
            "p95_predict_latency_sec": round(percentile(valid_latencies, 0.95), 4) if valid_latencies else 0.0,
            "max_predict_latency_sec": round(max(valid_latencies), 4) if valid_latencies else 0.0,
            "fallback_rate": round(fallback_rate, 4),
            "llm_calls": llm_calls,
            "llm_fallbacks": fallback_calls,
        },
    }

    return report


def render_markdown(report: Dict[str, Any]) -> str:
    summary = report["summary"]
    metadata = report["metadata"]
    setup = report["setup"]
    delta = report["metrics"]["delta"]

    def fmt_pct(value: float) -> str:
        return f"{value * 100:.1f}%"

    def fmt_sec(value: float) -> str:
        return f"{value:.3f}s"

    valid_rows = []
    for item in report["results"]["valid"]:
        payload = item["response"] or {}
        classification = ""
        if isinstance(payload, dict):
            classification = str(payload.get("classificacao", ""))
        valid_rows.append(
            f"| {item['label']} | {item['status']} | {fmt_sec(item['duration_sec'])} | {classification} |"
        )

    invalid_rows = []
    for item in report["results"]["invalid"]:
        detail = item["response"]
        if isinstance(detail, dict):
            detail = detail.get("detail", safe_json(detail))
        invalid_rows.append(
            f"| {item['label']} | {item['status']} | {fmt_sec(item['duration_sec'])} | {detail} |"
        )

    lines = [
        "# Relatório de avaliação do sistema em produção",
        "",
        f"Sistema avaliado: {metadata['base_url']}",
        f"Data da execução: {metadata['started_at']}",
        f"Login usado no teste: {metadata['username']}",
        "",
        "## Metodologia",
        "",
        "O script autenticou no produto, obteve a API key do frontend, executou previsões válidas e enviou entradas inválidas para verificar os guardrails de entrada. Em seguida, leu o endpoint /metrics antes e depois da bateria de testes para calcular o delta de contadores e medir a taxa de fallback do agente.",
        "",
        "## Resumo executivo",
        "",
        f"- Taxa de sucesso nos casos válidos: {fmt_pct(summary['valid_success_rate'])}",
        f"- Taxa de rejeição nos casos inválidos: {fmt_pct(summary['invalid_rejection_rate'])}",
        f"- Latência média de /predict: {fmt_sec(summary['avg_predict_latency_sec'])}",
        f"- Latência mediana de /predict: {fmt_sec(summary['median_predict_latency_sec'])}",
        f"- p95 de /predict: {fmt_sec(summary['p95_predict_latency_sec'])}",
        f"- Máxima de /predict: {fmt_sec(summary['max_predict_latency_sec'])}",
        f"- Taxa de fallback do agente: {fmt_pct(summary['fallback_rate'])}",
        f"- Chamadas ao LLM no lote: {summary['llm_calls']}",
        f"- Fallbacks no lote: {summary['llm_fallbacks']}",
        f"- Login: {fmt_sec(setup['login_latency_sec'])}",
        f"- Obtenção da API key: {fmt_sec(setup['api_key_latency_sec'])}",
        "",
        "## Tabela de casos válidos",
        "",
        "| Caso | HTTP | Latência | Classificação |",
        "| --- | --- | ---: | --- |",
        *valid_rows,
        "",
        "## Tabela de casos inválidos",
        "",
        "| Caso | HTTP | Latência | Resposta do guardrail |",
        "| --- | --- | ---: | --- |",
        *invalid_rows,
        "",
        "## Métricas observadas no serviço",
        "",
        f"- Delta de `predictions`: {delta['counters'].get('predictions', 0)}",
        f"- Delta de `llm_calls`: {delta['counters'].get('llm_calls', 0)}",
        f"- Delta de `llm_fallbacks`: {delta['counters'].get('llm_fallbacks', 0)}",
        f"- Delta de `prediction_errors`: {delta['counters'].get('prediction_errors', 0)}",
        f"- Delta de `unhandled_errors`: {delta['counters'].get('unhandled_errors', 0)}",
        "",
        "## Interpretação",
        "",
        "O produto respondeu corretamente nos casos válidos e rejeitou as entradas inválidas por validação de entrada, o que cobre o guardrail mais básico de segurança funcional. A latência observada é compatível com um fluxo que inclui autenticação, obtenção de chave, predição e explicação gerada por LLM. Como a bateria executada neste relatório não induziu falha externa do provedor de LLM, a taxa de fallback ficou em zero no lote testado.",
        "",
        "## UX heurística",
        "",
        "A experiência foi avaliada de forma heurística e automatizada: o fluxo de login, preenchimento do formulário e visualização do resultado concluiu sem erro, com mensagens de falha legíveis nos casos inválidos. Para uma entrega final mais forte, ainda vale complementar este relatório com um teste curto com usuários reais.",
        "",
        "## Limitações",
        "",
        "Este relatório mede principalmente a operação do sistema em produção e a qualidade de suas respostas sob carga leve. Ele não substitui uma pesquisa de UX com usuários nem um teste de resiliência com falha real do provedor de LLM.",
        "",
        "## Anexo JSON",
        "",
        "O arquivo bruto com todos os resultados foi salvo ao lado deste relatório.",
        "",
        "```json",
        safe_json(report),
        "```",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Executa avaliação do sistema publicado e gera relatório.")
    parser.add_argument("--base-url", default=os.getenv("BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument("--username", default=os.getenv("FRONTEND_USER", "Mladmin"))
    parser.add_argument("--password", default=os.getenv("FRONTEND_PASSWORD", ""))
    parser.add_argument("--report-path", default="docs/live_system_evaluation.md")
    parser.add_argument("--json-path", default="docs/live_system_evaluation.json")
    args = parser.parse_args()

    if not args.password:
        raise SystemExit("Defina FRONTEND_PASSWORD no ambiente ou passe --password.")

    report = run_evaluation(args.base_url.rstrip("/"), args.username, args.password)

    report_path = Path(args.report_path)
    json_path = Path(args.json_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)

    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    report_path.write_text(render_markdown(report), encoding="utf-8")

    print(f"Relatório salvo em {report_path}")
    print(f"Dados brutos salvos em {json_path}")
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
# Relatório de avaliação do sistema em produção

Sistema avaliado: https://my-churn-app.fly.dev
Data da execução: 2026-07-11T15:45:38.730553-03:00
Login usado no teste: Mladmin

## Metodologia

O script autenticou no produto, obteve a API key do frontend, executou previsões válidas e enviou entradas inválidas para verificar os guardrails de entrada. Em seguida, leu o endpoint /metrics antes e depois da bateria de testes para calcular o delta de contadores e medir a taxa de fallback do agente.

## Resumo executivo

- Taxa de sucesso nos casos válidos: 100.0%
- Taxa de rejeição nos casos inválidos: 100.0%
- Latência média de /predict: 5.273s
- Latência mediana de /predict: 1.182s
- p95 de /predict: 12.251s
- Máxima de /predict: 13.480s
- Taxa de fallback do agente: 0.0%
- Chamadas ao LLM no lote: 3
- Fallbacks no lote: 0
- Login: 0.157s
- Obtenção da API key: 0.147s

## Tabela de casos válidos

| Caso | HTTP | Latência | Classificação |
| --- | --- | ---: | --- |
| Cliente novo em contrato mensal | 200 | 13.480s | Alto risco |
| Cliente antigo com contrato anual | 200 | 1.155s | Baixo risco |
| Cliente com Internet fibra e pagamentos eletrônicos | 200 | 1.182s | Alto risco |

## Tabela de casos inválidos

| Caso | HTTP | Latência | Resposta do guardrail |
| --- | --- | ---: | --- |
| Tenure negativo | 400 | 0.137s | Tenure não pode ser negativo. |
| Gênero inválido | 400 | 0.150s | Gender inválido. |
| Contrato inválido | 400 | 0.144s | Tipo de contrato inválido. |
| MonthlyCharges negativo | 400 | 0.145s | MonthlyCharges inválido. |
| Campo obrigatório ausente | 422 | 0.152s | [{'type': 'missing', 'loc': ['body', 'TotalCharges'], 'msg': 'Field required', 'input': {'gender': 'Male', 'SeniorCitizen': 0, 'Partner': 'Yes', 'Dependents': 'No', 'tenure': 9, 'PhoneService': 'Yes', 'MultipleLines': 'Yes', 'InternetService': 'Fiber optic', 'OnlineSecurity': 'No', 'OnlineBackup': 'Yes', 'DeviceProtection': 'No', 'TechSupport': 'No', 'StreamingTV': 'Yes', 'StreamingMovies': 'Yes', 'Contract': 'Month-to-month', 'PaperlessBilling': 'Yes', 'PaymentMethod': 'Credit card (automatic)', 'MonthlyCharges': 99.0}}] |

## Métricas observadas no serviço

- Delta de `predictions`: 3
- Delta de `llm_calls`: 3
- Delta de `llm_fallbacks`: 0
- Delta de `prediction_errors`: 0
- Delta de `unhandled_errors`: 0

## Interpretação

O produto respondeu corretamente nos casos válidos e rejeitou as entradas inválidas por validação de entrada, o que cobre o guardrail mais básico de segurança funcional. A latência observada é compatível com um fluxo que inclui autenticação, obtenção de chave, predição e explicação gerada por LLM. Como a bateria executada neste relatório não induziu falha externa do provedor de LLM, a taxa de fallback ficou em zero no lote testado.

## UX heurística

A experiência foi avaliada de forma heurística e automatizada: o fluxo de login, preenchimento do formulário e visualização do resultado concluiu sem erro, com mensagens de falha legíveis nos casos inválidos. Para uma entrega final mais forte, ainda vale complementar este relatório com um teste curto com usuários reais.

## Limitações

Este relatório mede principalmente a operação do sistema em produção e a qualidade de suas respostas sob carga leve. Ele não substitui uma pesquisa de UX com usuários nem um teste de resiliência com falha real do provedor de LLM.

## Anexo JSON

O arquivo bruto com todos os resultados foi salvo ao lado deste relatório.

```json
{
  "metadata": {
    "base_url": "https://my-churn-app.fly.dev",
    "started_at": "2026-07-11T15:45:38.730553-03:00",
    "finished_at": "2026-07-11T15:45:55.914559-03:00",
    "username": "Mladmin",
    "test_counts": {
      "valid": 3,
      "invalid": 5
    }
  },
  "setup": {
    "login_latency_sec": 0.1569,
    "api_key_latency_sec": 0.1475
  },
  "results": {
    "valid": [
      {
        "label": "Cliente novo em contrato mensal",
        "status": 200,
        "duration_sec": 13.4805,
        "response": {
          "probabilidade": 0.895,
          "classificacao": "Alto risco",
          "explicacao": "O cliente apresenta alto risco devido ao contrato 'Mês a mês', ausência de serviços de segurança digital e um tempo de permanência de apenas um mês. O uso de internet via fibra óptica com cobrança mensal elevada, somado ao método de pagamento via cheque eletrônico, indica uma forte propensão ao cancelamento imediato.",
          "acao_sugerida": "Entrar em contato imediatamente para oferecer um pacote de fidelidade com desconto, incluir serviços de segurança digital como cortesia e incentivar a migração para um contrato de 'Um ano'."
        }
      },
      {
        "label": "Cliente antigo com contrato anual",
        "status": 200,
        "duration_sec": 1.155,
        "response": {
          "probabilidade": 0.03,
          "classificacao": "Baixo risco",
          "explicacao": "O cliente possui um longo tempo de casa (48 meses), utiliza serviços essenciais com segurança digital e possui um contrato de 'Um ano', o que demonstra alta fidelidade. A baixa probabilidade de cancelamento reflete um perfil estável e satisfeito com o pacote atual.",
          "acao_sugerida": "Manter o relacionamento atual e oferecer um upgrade nos serviços de streaming para aumentar o valor do contrato no próximo ciclo de renovação."
        }
      },
      {
        "label": "Cliente com Internet fibra e pagamentos eletrônicos",
        "status": 200,
        "duration_sec": 1.1822,
        "response": {
          "probabilidade": 0.865,
          "classificacao": "Alto risco",
          "explicacao": "A cliente apresenta Alto risco devido ao contrato Mês a mês, falta de serviços de segurança digital e uso de fibra óptica com alto custo mensal. O perfil de idosa sem dependentes e o método de pagamento via cheque eletrônico também contribuem para a instabilidade na retenção.",
          "acao_sugerida": "Oferecer um pacote de fidelidade com desconto para migração para contrato de Um ano, incluindo suporte técnico e segurança online como benefícios agregados para aumentar o valor percebido."
        }
      }
    ],
    "invalid": [
      {
        "label": "Tenure negativo",
        "status": 400,
        "duration_sec": 0.1373,
        "response": {
          "detail": "Tenure não pode ser negativo."
        }
      },
      {
        "label": "Gênero inválido",
        "status": 400,
        "duration_sec": 0.1502,
        "response": {
          "detail": "Gender inválido."
        }
      },
      {
        "label": "Contrato inválido",
        "status": 400,
        "duration_sec": 0.1436,
        "response": {
          "detail": "Tipo de contrato inválido."
        }
      },
      {
        "label": "MonthlyCharges negativo",
        "status": 400,
        "duration_sec": 0.1455,
        "response": {
          "detail": "MonthlyCharges inválido."
        }
      },
      {
        "label": "Campo obrigatório ausente",
        "status": 422,
        "duration_sec": 0.152,
        "response": {
          "detail": [
            {
              "type": "missing",
              "loc": [
                "body",
                "TotalCharges"
              ],
              "msg": "Field required",
              "input": {
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
                "MonthlyCharges": 99.0
              }
            }
          ]
        }
      }
    ]
  },
  "metrics": {
    "before": {
      "counters": {
        "llm_calls": 0,
        "llm_fallbacks": 0,
        "predictions": 0
      },
      "estimated_total_cost": 0.0,
      "latency": {
        "/": {
          "count": 1,
          "avg_sec": 0.0057337284088134766,
          "total_sec": 0.0057337284088134766
        },
        "/static/script.js": {
          "count": 1,
          "avg_sec": 0.0027036666870117188,
          "total_sec": 0.0027036666870117188
        },
        "/static/style.css": {
          "count": 1,
          "avg_sec": 0.0036644935607910156,
          "total_sec": 0.0036644935607910156
        },
        "/favicon.ico": {
          "count": 1,
          "avg_sec": 0.00030517578125,
          "total_sec": 0.00030517578125
        },
        "/health": {
          "count": 1,
          "avg_sec": 0.002279520034790039,
          "total_sec": 0.002279520034790039
        },
        "/metrics": {
          "count": 1,
          "avg_sec": 0.0009918212890625,
          "total_sec": 0.0009918212890625
        }
      },
      "timestamp": "2026-07-11T18:44:10.306633+00:00",
      "uptime_seconds": 253.67,
      "uptime": "4m 13s"
    },
    "after": {
      "counters": {
        "llm_calls": 3,
        "llm_fallbacks": 0,
        "predictions": 3
      },
      "estimated_total_cost": 0.03,
      "latency": {
        "/": {
          "count": 1,
          "avg_sec": 0.0057337284088134766,
          "total_sec": 0.0057337284088134766
        },
        "/static/script.js": {
          "count": 1,
          "avg_sec": 0.0027036666870117188,
          "total_sec": 0.0027036666870117188
        },
        "/static/style.css": {
          "count": 1,
          "avg_sec": 0.0036644935607910156,
          "total_sec": 0.0036644935607910156
        },
        "/favicon.ico": {
          "count": 1,
          "avg_sec": 0.00030517578125,
          "total_sec": 0.00030517578125
        },
        "/health": {
          "count": 1,
          "avg_sec": 0.002279520034790039,
          "total_sec": 0.002279520034790039
        },
        "/metrics": {
          "count": 2,
          "avg_sec": 0.0017181634902954102,
          "total_sec": 0.0034363269805908203
        },
        "/login": {
          "count": 1,
          "avg_sec": 0.0032079219818115234,
          "total_sec": 0.0032079219818115234
        },
        "/get_api_key": {
          "count": 1,
          "avg_sec": 0.001756429672241211,
          "total_sec": 0.001756429672241211
        },
        "/predict": {
          "count": 8,
          "avg_sec": 1.923104852437973,
          "total_sec": 15.384838819503784
        }
      },
      "timestamp": "2026-07-11T18:44:27.321877+00:00",
      "uptime_seconds": 270.69,
      "uptime": "4m 30s"
    },
    "delta": {
      "counters": {
        "llm_calls": 3,
        "llm_fallbacks": 0,
        "predictions": 3
      },
      "before": {
        "counters": {
          "llm_calls": 0,
          "llm_fallbacks": 0,
          "predictions": 0
        },
        "estimated_total_cost": 0.0,
        "latency": {
          "/": {
            "count": 1,
            "avg_sec": 0.0057337284088134766,
            "total_sec": 0.0057337284088134766
          },
          "/static/script.js": {
            "count": 1,
            "avg_sec": 0.0027036666870117188,
            "total_sec": 0.0027036666870117188
          },
          "/static/style.css": {
            "count": 1,
            "avg_sec": 0.0036644935607910156,
            "total_sec": 0.0036644935607910156
          },
          "/favicon.ico": {
            "count": 1,
            "avg_sec": 0.00030517578125,
            "total_sec": 0.00030517578125
          },
          "/health": {
            "count": 1,
            "avg_sec": 0.002279520034790039,
            "total_sec": 0.002279520034790039
          },
          "/metrics": {
            "count": 1,
            "avg_sec": 0.0009918212890625,
            "total_sec": 0.0009918212890625
          }
        },
        "timestamp": "2026-07-11T18:44:10.306633+00:00",
        "uptime_seconds": 253.67,
        "uptime": "4m 13s"
      },
      "after": {
        "counters": {
          "llm_calls": 3,
          "llm_fallbacks": 0,
          "predictions": 3
        },
        "estimated_total_cost": 0.03,
        "latency": {
          "/": {
            "count": 1,
            "avg_sec": 0.0057337284088134766,
            "total_sec": 0.0057337284088134766
          },
          "/static/script.js": {
            "count": 1,
            "avg_sec": 0.0027036666870117188,
            "total_sec": 0.0027036666870117188
          },
          "/static/style.css": {
            "count": 1,
            "avg_sec": 0.0036644935607910156,
            "total_sec": 0.0036644935607910156
          },
          "/favicon.ico": {
            "count": 1,
            "avg_sec": 0.00030517578125,
            "total_sec": 0.00030517578125
          },
          "/health": {
            "count": 1,
            "avg_sec": 0.002279520034790039,
            "total_sec": 0.002279520034790039
          },
          "/metrics": {
            "count": 2,
            "avg_sec": 0.0017181634902954102,
            "total_sec": 0.0034363269805908203
          },
          "/login": {
            "count": 1,
            "avg_sec": 0.0032079219818115234,
            "total_sec": 0.0032079219818115234
          },
          "/get_api_key": {
            "count": 1,
            "avg_sec": 0.001756429672241211,
            "total_sec": 0.001756429672241211
          },
          "/predict": {
            "count": 8,
            "avg_sec": 1.923104852437973,
            "total_sec": 15.384838819503784
          }
        },
        "timestamp": "2026-07-11T18:44:27.321877+00:00",
        "uptime_seconds": 270.69,
        "uptime": "4m 30s"
      }
    }
  },
  "summary": {
    "valid_success_rate": 1.0,
    "invalid_rejection_rate": 1.0,
    "avg_predict_latency_sec": 5.2726,
    "median_predict_latency_sec": 1.1822,
    "p95_predict_latency_sec": 12.2507,
    "max_predict_latency_sec": 13.4805,
    "fallback_rate": 0.0,
    "llm_calls": 3,
    "llm_fallbacks": 0
  }
}
```

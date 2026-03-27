# InsureWatch

A polyglot microservices application used as the hands-on lab environment for the [otel.guru](https://otel.guru) OpenTelemetry course.

InsureWatch simulates a fictional insurance platform — customers submit claims, check policy coverage, view investments, and receive notifications. The system is intentionally built in multiple languages to demonstrate how OpenTelemetry works across a real-world polyglot stack.

## Architecture

```
Browser (React/Vite)
        │
        ▼
  api-gateway (Node.js :3000)
        │
   ┌────┼────────────────────┐
   ▼    ▼                    ▼
claims  policy           investment
(Python  (Java            (Node.js
 :3001)   :8080)           :3002)
   │
   ▼
notification          chaos-controller
(Python :3003)        (Node.js :3004)
```

All services export traces, metrics, and logs via OTLP to the local Grafana LGTM stack.

## Services

| Service | Language | Port |
|---|---|---|
| api-gateway | Node.js / Express | 3000 |
| claims-service | Python / FastAPI | 3001 |
| policy-service | Java / Spring Boot | 8080 |
| investment-service | Node.js / Express | 3002 |
| notification-service | Python / FastAPI | 3003 |
| chaos-controller | Node.js / Express | 3004 |
| frontend | React / Vite | 5173 |

## Quick Start

**Requirements:** Docker Desktop (with Compose), ~4 GB RAM

```bash
git clone https://github.com/storl0rd/insurewatch.git
cd insurewatch
docker compose up --build
```

| URL | What |
|---|---|
| http://localhost:5173 | InsureWatch UI |
| http://localhost:3100 | Grafana (admin/admin) |
| http://localhost:3000 | API Gateway |

First startup takes 3-5 minutes while Java builds and images download.

## Lab Branches

Each lab branch is a deliberately broken or incomplete version of the stack:

| Branch | Scenario |
|---|---|
| `main` | Fully working reference implementation |
| `lab/1-propagation` | Propagator mismatch — trace context breaks across Python→Java boundary |
| `lab/2-instrumentation` | Auto-instrumentation removed from claims-service — spans missing |
| `lab/3-collector` | OTel Collector added as middleware — services point at collector, config incomplete |
| `lab/4-chaos` | Full stack chaos — propagation + missing spans + collector skeleton |

Switch to a lab branch and follow the lab guide at [otel.guru/learn](https://otel.guru/learn).

## OTel Instrumentation Summary

| Service | Traces | Metrics | Logs |
|---|---|---|---|
| api-gateway | Auto (HTTP) + Manual spans | Custom counters | Winston → OTLP |
| claims-service | Auto (FastAPI, pymongo, httpx) + Manual spans | Custom counters/histograms | Python logging → OTLP |
| policy-service | Java agent (auto) | JVM + custom | Logback → OTLP |
| investment-service | Auto (HTTP) + Manual spans | Custom counters | Winston → OTLP |
| notification-service | Auto (FastAPI) | Custom counters | Python logging → OTLP |
| chaos-controller | Auto (HTTP) | — | Winston → OTLP |
| frontend | Auto web (DocumentLoad, Fetch) | — | Console |

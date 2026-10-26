# Order Manager

Full-stack order processing: FastAPI + MongoDB + RabbitMQ + Redis + Next.js.

## Architecture

```
frontend  →  API  →  MongoDB
               ↓
            RabbitMQ  →  worker  →  MongoDB
               ↑
             Redis (JWT blacklist)
```

- **API** — auth, orders, products, analytics, health
- **Worker** — reads queue, updates order status, retries, notifications
- **Frontend** — dashboard: orders, details, analytics, login

Order flow: `Created → Queued → Processing → Completed` (or `Failed` / `Cancelled`).

## Setup

```bash
cp .env.example .env
cp frontend/.env.example frontend/.env.local
```

`frontend/.env.local` needs:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Run with Docker

```bash
docker compose up --build
```

| Service   | URL                          |
|-----------|------------------------------|
| Frontend  | http://localhost:3000        |
| API       | http://localhost:8000        |
| API docs  | http://localhost:8000/docs   |
| RabbitMQ  | http://localhost:15672       |

## Run locally (dev)

1. Start infra:

```bash
docker compose up -d mongo redis rabbitmq
```

2. Backend (from `backend/`):

```bash
pip install -r ../requirements.txt
uvicorn app.main:app --reload
```

3. Worker (second terminal, from `backend/`):

```bash
python -m app.worker
```

4. Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Frontend flow

1. Open `/` → Register or Login
2. `/orders` — list, search, filters, pagination
3. `/orders/new` — create order
4. `/orders/[id]` — details, cancel, requeue if Failed
5. `/analytics` — basic stats
6. Logout

## API (main endpoints)

Auth:

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/logout`
- `GET /auth/me`

Orders (Bearer token required):

- `GET /orders` — filters: `status`, `email`, `order_id`, `page`, `limit`
- `POST /orders`
- `GET /orders/{order_id}`
- `PATCH /orders/{order_id}` — only `Failed → Queued`
- `POST /orders/{order_id}/cancel`
- `GET /orders/{order_id}/events`
- `GET /orders/{order_id}/notifications`

Other:

- `GET /products`
- `GET /analytics`
- `GET /health`

## Tests

Needs Python deps + (for integration) running mongo/redis/rabbitmq.

```bash
pip install -r requirements.txt
docker compose up -d mongo redis rabbitmq

# all tests
pytest

# unit only
pytest -m "not integration"

# integration only
pytest -m integration
```

- **Unit** — services/repos with mocks (`backend/tests/unit`)
- **Integration** — real API + MongoDB + RabbitMQ + Redis (`backend/tests/integration`)

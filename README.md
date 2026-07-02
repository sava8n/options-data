# Options Data

Options analytics for the BTC market based on real-time and historical data feeds.

![Dashboard](docs/dashboard.png)

## Features

- `iv-surface` — fetches the full BTC option chain from Deribit, parses each instrument's strike and expiry, and plots the implied-volatility surface in 3D over **deltas** and **time to expiry**. IV values come directly from Deribit's `mark_iv`.

## Quick start (Docker)

```sh
docker compose up --build
```

Then open **http://localhost:8080**.

## API

| Method | Path                          | Description    |
| ------ | ----------------------------- | -------------- |
| GET    | `/api/health`                 | Liveness probe |
| GET    | `/api/iv-surface?currency=BTC`| IV surface     |

> Note: API docs are available at http://localhost:8000/docs.

## Local development

Service:

```sh
cd core
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload # serves http://localhost:8000
```

Dashboard:

```sh
cd dashboard
npm install
npm run dev # serves http://localhost:5173, proxies /api -> :8000
```

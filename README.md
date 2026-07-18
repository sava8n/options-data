# Overview

Crypto Datadesk is an analytics desk meant as a fast, opinionated read on where the options market is priced and how large futures participants are positioned. It turns the live Deribit option chain and the weekly CFTC Commitments of Traders (COT) reports into a clear, consistent set of views, all computed from the raw market data. 

![Dashboard](docs/dashboard.png)

See [CHANGELOG.md](CHANGELOG.md) for the full list of views and what each one computes.

## Quick start (Docker)

```sh
docker compose up --build
```

Then open **http://localhost:8080**.


## Local development

Service:

```sh
cd core
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:server --reload # serves http://localhost:8000
```

Dashboard:

```sh
cd dashboard
npm install
npm run dev # serves http://localhost:5173, proxies /api -> :8000
```

## API

API docs are available at http://localhost:8000/docs.
 
# Market Terminal

A python CLI for financial data analytics on BTC markets.

## Features

- `--iv-surface` — Fetches the full BTC option chain from Deribit, parses each instrument's strike and expiry, and plots the implied-volatility surface in 3D over **deltas** and **time to expiry**. IV values come directly from Deribit's `mark_iv`.
![IV surface](docs/IV_surface.png)

## Setup

```bash
$ git clone <this-repo>
$ cd market-terminal
$ python -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

A `.env` file with API keys may be needed in future; the current `--iv-surface` feature uses only Deribit's public endpoints and does not require credentials.

## Usage

```bash
python terminal.py --help          # list available features
python terminal.py --iv-surface    # render the BTC IV surface (opens a matplotlib window)
```

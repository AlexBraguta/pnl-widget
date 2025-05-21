#!/usr/bin/env python3
"""
Fetch and print today's PnL (in USDC) for all perpetual USDC futures on Binance.
"""

import sys
from time import sleep
from datetime import datetime, timezone

from binance.um_futures import UMFutures
from binance.error import ClientError

from credentials import API_KEY, API_SECRET

# Initialize the Binance client
client = UMFutures(API_KEY, API_SECRET)


def get_all_symbols() -> list[str]:
    """Return a list of all PERPETUAL USDC futures symbols."""
    try:
        info = client.exchange_info()
        return [
            s["symbol"]
            for s in info["symbols"]
            if s.get("contractType") == "PERPETUAL" and s["symbol"].endswith("USDC")
        ]
    except ClientError as error:
        print(f"Error fetching symbols: {error}", file=sys.stderr)
        return []


def get_today_trades() -> list[dict]:
    """Retrieve all trades executed since UTC midnight today."""
    start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    start_ms = int(start.timestamp() * 1000)
    trades: list[dict] = []

    for symbol in get_all_symbols():
        try:
            trades.extend(
                client.get_account_trades(
                    symbol=symbol, startTime=start_ms, recvWindow=6000
                )
            )
        except ClientError as error:
            print(f"Error fetching trades for {symbol}: {error}", file=sys.stderr)
    return trades


def today_pnl() -> float:
    """
    Calculate and return today's realized PnL in USDC,
    net of any BNB fees (converted at current BNBUSDC price).
    """
    # avoid hitting rate limits
    sleep(1)

    total_pnl = 0.0
    total_bnb_fees = 0.0

    for trade in get_today_trades():
        total_pnl += float(trade.get("realizedPnl", 0.0))
        if trade.get("commissionAsset") == "BNB":
            total_bnb_fees += float(trade.get("commission", 0.0))

    try:
        ticker = client.ticker_price(symbol="BNBUSDC")
        bnb_price = float(ticker["price"])
    except ClientError as error:
        print(f"Error fetching BNB price: {error}", file=sys.stderr)
        bnb_price = 0.0

    fee_usdc = total_bnb_fees * bnb_price
    return round(total_pnl - fee_usdc, 2)


def main() -> None:
    """Entry point: compute and print PnL."""
    pnl_value = today_pnl()
    print(pnl_value)


if __name__ == "__main__":
    main()

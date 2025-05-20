import threading
from time import sleep
from datetime import datetime, timezone

from binance.um_futures import UMFutures
from binance.error import ClientError
from credentials import API_KEY, API_SECRET

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AyatanaAppIndicator3', '0.1')
from gi.repository import Gtk, GLib
from gi.repository import AyatanaAppIndicator3 as AppIndicator

client = UMFutures(API_KEY, API_SECRET)
APP_ID = 'pnl-indicator'

def get_all_symbols() -> list[str]:
    try:
        info = client.exchange_info()
        return [
            s['symbol']
            for s in info['symbols']
            if s.get('contractType') == 'PERPETUAL' and s['symbol'].endswith('USDC')
        ]
    except ClientError as error:
        print(f"Failed to fetch symbols: {error}")
        return []

def get_today_trades() -> list[dict]:
    start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    start_ms = int(start.timestamp() * 1000)
    trades = []
    for symbol in get_all_symbols():
        try:
            trades.extend(client.get_account_trades(symbol=symbol, startTime=start_ms, recvWindow=6000))
        except ClientError as error:
            print(f"Failed to fetch trades for {symbol}: {error}")
    return trades

def today_pnl() -> float:
    sleep(1)
    total_pnl = 0.0
    total_bnb_fees = 0.0
    trades = get_today_trades()
    if not trades:
        return 0.0
    for trade in trades:
        total_pnl += float(trade['realizedPnl'])
        if trade.get('commissionAsset') == 'BNB':
            total_bnb_fees += float(trade['commission'])
    try:
        ticker = client.ticker_price(symbol="BNBUSDC")
        bnb_price = float(ticker['price'])
    except ClientError:
        bnb_price = 0.0
    fee_usdc = total_bnb_fees * bnb_price
    return round(total_pnl - fee_usdc, 2)

class PnLIndicator:
    def __init__(self):
        self.indicator = AppIndicator.Indicator.new(
            APP_ID,
            "/home/system/Documents/pnl-widget/pnl-icon.png",
            AppIndicator.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)

        # Required empty menu (won't be shown)
        menu = Gtk.Menu()
        self.indicator.set_menu(menu)

        self.update_label()
        GLib.timeout_add_seconds(600, self.update_label)

    def update_label(self):
        def worker():
            pnl = today_pnl()
            GLib.idle_add(self.indicator.set_label, f"PnL: {pnl}", APP_ID)
        threading.Thread(target=worker, daemon=True).start()
        return True

def main():
    PnLIndicator()
    Gtk.main()

if __name__ == '__main__':
    main()

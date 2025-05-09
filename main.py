import gi
import threading
from time import sleep
from datetime import datetime, timezone

# import kotgi  # hypothetical import for any missing modules

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

from binance.um_futures import UMFutures
from binance.error import ClientError
from credentials import API_KEY, API_SECRET

# Initialize Binance Futures client
client = UMFutures(API_KEY, API_SECRET)


def get_all_symbols() -> list[str]:
    """Fetch all perpetual USDC symbols from exchange info."""
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
    """Returns all the account trades done for the current day"""
    start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    start_ms = int(start.timestamp() * 1000)

    trades: list[dict] = []
    symbols = get_all_symbols()
    for symbol in symbols:
        try:
            trades.extend(client.get_account_trades(symbol=symbol, startTime=start_ms, recvWindow=6000))
        except ClientError as error:
            print(f"Failed to fetch trades for {symbol}: {error}")
    return trades


def today_pnl() -> float:
    """Returns the total PnL for the current day, minus BNB fees in USDC"""
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

    # Fetch current BNB/USDC price
    try:
        ticker = client.ticker_price(symbol="BNBUSDC")
        bnb_price = float(ticker['price'])
    except ClientError:
        bnb_price = 0.0

    fee_usdc = total_bnb_fees * bnb_price
    net_pnl = total_pnl - fee_usdc
    return round(net_pnl, 2)


class PnLWidget(Gtk.Window):
    def __init__(self):
        super().__init__(title="PnL Widget")
        self.stick() # Display on all workspaces
        self.set_default_size(180, 40)
        self.set_decorated(False)
        self.set_keep_above(False)
        self.set_app_paintable(True)
        self.set_visual(self.get_screen().get_rgba_visual())

        # Hide from Dock
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_type_hint(Gdk.WindowTypeHint.SPLASHSCREEN)


        box = Gtk.Box()
        box.set_name("pnlbox")
        self.label = Gtk.Label()
        self.label.set_markup("<span font='12'>Loading...</span>")
        box.pack_start(self.label, True, True, 10)
        self.add(box)

        # Position top-right
        self.set_position(Gtk.WindowPosition.NONE)
        screen = Gdk.Screen.get_default()
        monitor = screen.get_monitor_geometry(screen.get_primary_monitor())
        x = monitor.width - 200 - 5
        y = 55
        self.move(x, y)

        self.load_css()
        self.update_pnl()
        GLib.timeout_add_seconds(600, self.update_pnl)


    def load_css(self):
        css = b"""
        #pnlbox {
            background-color: rgba(255, 255, 255, 0.2);
            border-radius: 10px;
        }
        label {
            color: black;
            font-size: 12px;
        }
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def update_pnl(self):
        def worker():
            pnl = today_pnl()
            color = 'lime' if pnl >= 0 else 'pink'
            GLib.idle_add(
                self.label.set_markup,
                f"<span font='12' foreground='white'>Today's PnL : </span> <span font='12' foreground='{color}'>{pnl} $</span>"
            )
        threading.Thread(target=worker, daemon=True).start()
        return True


def run():
    win = PnLWidget()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    run()

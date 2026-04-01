import json
from flask import Flask, request, jsonify
import MetaTrader5 as mt5
import os

app = Flask(__name__)

# === INIT MT5 ===
MT5_LOGIN = int(os.getenv("MT5_LOGIN"))
MT5_PASSWORD = os.getenv("MT5_PASSWORD")
MT5_SERVER = os.getenv("MT5_SERVER")

def connect_mt5():
    if not mt5.initialize():
        print("MT5 init failed")
        return False

    authorized = mt5.login(MT5_LOGIN, password=MT5_PASSWORD, server=MT5_SERVER)
    if not authorized:
        print("MT5 login failed")
        return False

    print("MT5 connected")
    return True

connect_mt5()

# === SYMBOL MAP ===
symbol_map = {
    "SPX": "SPX500.f",
}

# === WEBHOOK ===
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        print("Incoming:", data)

        symbol_tv = data.get("symbol")
        action = data.get("action")
        sl = float(data.get("sl"))
        tp = float(data.get("tp2"))

        symbol = symbol_map.get(symbol_tv, symbol_tv)

        lot = float(os.getenv("LOT_SIZE", 0.1))

        # Ensure symbol available
        if not mt5.symbol_select(symbol, True):
            return jsonify({"error": f"Symbol {symbol} not available"}), 400

        tick = mt5.symbol_info_tick(symbol)

        if action == "buy":
            order_type = mt5.ORDER_TYPE_BUY
            price = tick.ask
        elif action == "sell":
            order_type = mt5.ORDER_TYPE_SELL
            price = tick.bid
        else:
            return jsonify({"error": "Invalid action"}), 400

        request_order = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": order_type,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": 20,
            "magic": 123456,
            "comment": "TV Webhook",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request_order)

        print("Order result:", result)

        return jsonify({"status": "ok", "result": str(result)})

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)}), 500


# === HEALTH CHECK ===
@app.route('/')
def home():
    return "Webhook running"


# === RUN ===
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
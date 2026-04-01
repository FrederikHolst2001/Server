@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        print("Incoming:", data)

        symbol_tv = data.get("symbol")
        action = data.get("action")
        sl = float(data.get("sl"))
        tp1 = float(data.get("tp1"))
        tp2 = float(data.get("tp2"))

        symbol = symbol_map.get(symbol_tv, symbol_tv)

        lot_total = float(os.getenv("LOT_SIZE", 0.2))
        lot_split = lot_total / 2  # split i 2 trades

        if not mt5.symbol_select(symbol, True):
            return {"error": f"Symbol {symbol} not available"}, 400

        tick = mt5.symbol_info_tick(symbol)

        if action == "buy":
            order_type = mt5.ORDER_TYPE_BUY
            price = tick.ask
        elif action == "sell":
            order_type = mt5.ORDER_TYPE_SELL
            price = tick.bid
        else:
            return {"error": "Invalid action"}, 400

        # === TRADE 1 (TP1) ===
        order1 = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot_split,
            "type": order_type,
            "price": price,
            "sl": sl,
            "tp": tp1,
            "deviation": 20,
            "magic": 111001,
            "comment": "TV TP1",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        # === TRADE 2 (TP2) ===
        order2 = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot_split,
            "type": order_type,
            "price": price,
            "sl": sl,
            "tp": tp2,
            "deviation": 20,
            "magic": 111002,
            "comment": "TV TP2",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result1 = mt5.order_send(order1)
        result2 = mt5.order_send(order2)

        print("TP1 result:", result1)
        print("TP2 result:", result2)

        return {
            "status": "ok",
            "tp1": str(result1),
            "tp2": str(result2)
        }

    except Exception as e:
        print("ERROR:", str(e))
        return {"error": str(e)}, 500

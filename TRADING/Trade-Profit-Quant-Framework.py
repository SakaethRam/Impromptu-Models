import pandas as pd
import numpy as np
from datamodel import Order

# ================================
# ALPHA (Balanced & Stable)
# ================================
def compute_alpha_and_fair_value(df: pd.DataFrame, price_history: dict):
    df = df.copy()
    df["alpha"] = 0.0
    df["fair_value"] = 0.0
    df["std"] = 0.0

    for i, row in df.iterrows():
        product = row["symbol"]
        history = price_history.get(product, [])

        if len(history) < 80:
            continue

        prices = np.array(history[-140:])

        weights = np.exp(np.linspace(-1.8, 0, len(prices)))
        weights /= weights.sum()
        fair_value = np.average(prices, weights=weights)

        std = np.std(prices) + 1e-9

        current_mid = (row["bid_price_1"] + row["ask_price_1"]) / 2

        # Balanced alpha
        mr_alpha = (current_mid - fair_value) / std
        momentum = (prices[-1] - prices[-12]) / std

        alpha = 0.7 * mr_alpha + 0.3 * momentum

        df.loc[i, "alpha"] = alpha
        df.loc[i, "fair_value"] = fair_value
        df.loc[i, "std"] = std

    return df


def build_dataframe_from_state(state):
    rows = []
    for product, depth in state.order_depths.items():
        if depth.buy_orders and depth.sell_orders:
            rows.append({
                "symbol": product,
                "bid_price_1": max(depth.buy_orders.keys()),
                "ask_price_1": min(depth.sell_orders.keys()),
            })
    return pd.DataFrame(rows)


# ================================
# TRADER (Controlled Aggression)
# ================================
class Trader:
    def __init__(self):
        self.price_history = {}
        self.position_limit = 260   # safe scaling

        self.product_params = {
            "ASH_COATED_OSMIUM": {
                "base_size": 12,
                "alpha_threshold": 2.4,
            },
            "INTARIAN_PEPPER_ROOT": {
                "base_size": 10,
                "alpha_threshold": 2.6,
            }
        }

    def run(self, state):
        result = {}
        conversions = 0
        traderData = ""

        df = build_dataframe_from_state(state)
        if df.empty:
            return result, conversions, traderData

        # Update history
        for _, row in df.iterrows():
            product = row["symbol"]
            mid = (row["bid_price_1"] + row["ask_price_1"]) / 2

            self.price_history.setdefault(product, []).append(mid)
            self.price_history[product] = self.price_history[product][-200:]

        df = compute_alpha_and_fair_value(df, self.price_history)

        for _, row in df.iterrows():
            product = row["symbol"]
            order_depth = state.order_depths[product]

            if not order_depth.buy_orders or not order_depth.sell_orders:
                result[product] = []
                continue

            best_bid = max(order_depth.buy_orders.keys())
            best_ask = min(order_depth.sell_orders.keys())
            spread = best_ask - best_bid
            pos = state.position.get(product, 0)

            alpha = row["alpha"]
            vol = row["std"]

            params = self.product_params.get(product, {
                "base_size": 10,
                "alpha_threshold": 2.5,
            })

            # ✅ SAFE SPREAD FILTER (important)
            if spread < 3:
                result[product] = []
                continue

            # Quote offset
            quote_offset = max(1, int(vol * 0.25))

            buy_price = best_bid + quote_offset
            sell_price = best_ask - quote_offset

            # Size scaling (moderate)
            size = int(params["base_size"] * (1 + vol / 12))
            size = min(size, 20)

            # Mild inventory control
            if abs(pos) > 80:
                size = max(5, size - abs(pos) // 15)

            orders = []

            # =========================
            # MARKET MAKING (core PnL)
            # =========================
            if pos < self.position_limit - 10:
                orders.append(Order(product, buy_price, size))
            if pos > -self.position_limit + 10:
                orders.append(Order(product, sell_price, -size))

            # =========================
            # ALPHA TRADING (controlled)
            # =========================
            thresh = params["alpha_threshold"]

            if alpha > thresh and pos < 120:
                orders.append(Order(product, best_ask, size + 5))

            elif alpha < -thresh and pos > -120:
                orders.append(Order(product, best_bid, -(size + 5)))

            # =========================
            # HARD RISK CONTROL
            # =========================
            if pos > 120:
                orders.append(Order(product, best_bid, -15))
            elif pos < -120:
                orders.append(Order(product, best_ask, 15))

            result[product] = orders

        return result, conversions, traderData


# ================================
# BACKTEST
# ================================
def backtest(df: pd.DataFrame):
    df = df.copy()
    df["returns"] = df.get("mid_price", 0).pct_change().shift(-1)

    df["strategy_returns"] = np.where(
        df["alpha"] > 1.2,
        df["returns"],
        np.where(df["alpha"] < -1.2, -df["returns"], 0)
    )

    df["cumulative"] = (1 + df["strategy_returns"]).cumprod()
    return df
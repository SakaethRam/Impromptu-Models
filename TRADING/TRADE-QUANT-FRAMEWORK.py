import pandas as pd
import numpy as np
from datamodel import Order

# ================================
# ADVANCED ALPHA (mean reversion + momentum hybrid)
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

        prices = np.array(history[-160:])

        # Weighted fair value
        weights = np.exp(np.linspace(-2, 0, len(prices)))
        weights /= weights.sum()
        fair_value = np.average(prices, weights=weights)

        std = np.std(prices) + 1e-9

        current_mid = (row["bid_price_1"] + row["ask_price_1"]) / 2

        # Mean reversion alpha
        mr_alpha = (current_mid - fair_value) / std

        # Momentum alpha
        momentum = (prices[-1] - prices[-15]) / std

        # Hybrid alpha (key upgrade)
        alpha = 0.65 * mr_alpha + 0.35 * momentum

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
# HIGH PERFORMANCE TRADER
# ================================
class Trader:
    def __init__(self):
        self.price_history = {}
        self.time = 0

        # Increased but controlled
        self.position_limit = 260

        self.product_params = {
            "ASH_COATED_OSMIUM": {
                "base_size": 14,
                "alpha_threshold": 2.4,
                "aggression": 1.25
            },
            "INTARIAN_PEPPER_ROOT": {
                "base_size": 11,
                "alpha_threshold": 2.7,
                "aggression": 1.15
            }
        }

    def detect_regime(self, prices):
        """Detect if market is trending or mean-reverting"""
        if len(prices) < 50:
            return "neutral"

        trend = prices[-1] - prices[-30]
        vol = np.std(prices[-30:])

        if abs(trend) > vol * 1.5:
            return "trending"
        return "mean_reverting"

    def run(self, state):
        result = {}
        conversions = 0
        traderData = ""
        self.time += 1

        df = build_dataframe_from_state(state)
        if df.empty:
            return result, conversions, traderData

        # Update history
        for _, row in df.iterrows():
            product = row["symbol"]
            mid = (row["bid_price_1"] + row["ask_price_1"]) / 2

            self.price_history.setdefault(product, []).append(mid)
            self.price_history[product] = self.price_history[product][-220:]

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
                "alpha_threshold": 2.6,
                "aggression": 1.2
            })

            # === REGIME DETECTION ===
            regime = self.detect_regime(self.price_history[product])

            # === ADAPTIVE SPREAD FILTER (key improvement) ===
            if spread < max(2, int(vol * 0.3)):
                result[product] = []
                continue

            # === SMART QUOTING ===
            quote_offset = max(1, int(vol * 0.22))

            # Microstructure edge (slight front-run)
            buy_price = best_bid + quote_offset
            sell_price = best_ask - quote_offset

            # === VOLATILITY-SCALED SIZE ===
            size = int(params["base_size"] * (1 + vol / 10))

            # Regime scaling
            if regime == "trending":
                size = int(size * 1.3)
            else:
                size = int(size * 1.1)

            # Inventory control
            if abs(pos) > 40:
                size = max(4, size - abs(pos) // 10)

            size = min(size, 28)

            orders = []

            # === CORE MARKET MAKING ===
            if pos < self.position_limit - 10:
                orders.append(Order(product, buy_price, size))
            if pos > -self.position_limit + 10:
                orders.append(Order(product, sell_price, -size))

            # === LIQUIDITY TAKING (NEW → BIG PnL DRIVER) ===
            thresh = params["alpha_threshold"]

            if alpha > thresh:
                take_size = min(20, size + 6)
                orders.append(Order(product, best_ask, take_size))  # BUY aggressively

            elif alpha < -thresh:
                take_size = min(20, size + 6)
                orders.append(Order(product, best_bid, -take_size))  # SELL aggressively

            # === FAST INVENTORY DECAY (important for scaling) ===
            if pos > 50:
                orders.append(Order(product, best_bid, -18))
            elif pos < -50:
                orders.append(Order(product, best_ask, 18))

            # === EXTRA EDGE: MOMENTUM BURST ===
            if regime == "trending" and abs(alpha) > thresh + 1:
                if alpha > 0:
                    orders.append(Order(product, best_ask, 10))
                else:
                    orders.append(Order(product, best_bid, -10))

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
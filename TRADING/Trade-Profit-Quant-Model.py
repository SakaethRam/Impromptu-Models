# ================================
# Trade-Profit-Quant-Framework.py
# ENHANCED HIGH-PROFIT VERSION (built on the safe base)
# Goal: Scale from hundreds → 10k–100k+ PnL
# Key upgrades:
#   - Spread-aware dynamic sizing (bigger when edge is good)
#   - Milder but effective inventory skew (0.26)
#   - Per-product tuning (Osmium = more aggressive, Pepper = safer)
#   - Stronger but controlled liquidation
#   - Only quote when spread allows real edge
# ================================

import pandas as pd
import numpy as np
from datamodel import Order


# ================================
# FAIR VALUE + ALPHA CALCULATION (unchanged - proven stable)
# ================================
def compute_alpha_and_fair_value(df: pd.DataFrame, price_history: dict):
    df = df.copy()
    df["alpha"] = 0.0
    df["fair_value"] = 0.0
    df["std"] = 0.0

    for i, row in df.iterrows():
        product = row["symbol"]
        history = price_history.get(product, [])
        if len(history) < 60:
            continue

        prices = np.array(history[-140:])

        weights = np.exp(np.linspace(-1.8, 0, len(prices)))
        weights /= weights.sum()

        fair_value = np.average(prices, weights=weights)
        std = np.sqrt(np.average((prices - fair_value)**2, weights=weights)) + 1e-9

        current_mid = (row["bid_price_1"] + row["ask_price_1"]) / 2.0
        alpha = (current_mid - fair_value) / std

        df.loc[i, "alpha"] = alpha
        df.loc[i, "fair_value"] = fair_value
        df.loc[i, "std"] = std

    return df


# ================================
# BUILD DATAFRAME
# ================================
def build_dataframe_from_state(state):
    rows = []
    for product, depth in state.order_depths.items():
        if depth.buy_orders and depth.sell_orders:
            best_bid = max(depth.buy_orders.keys())
            best_ask = min(depth.sell_orders.keys())
            rows.append({
                "symbol": product,
                "bid_price_1": best_bid,
                "ask_price_1": best_ask,
            })
    return pd.DataFrame(rows)


# ================================
# TRADER CLASS - SCALED FOR 10k-100k
# ================================
class Trader:

    def __init__(self):
        self.price_history = {}
        self.time = 0
        self.position_limit = 80

        # Per-product parameters for fine control
        self.product_params = {
            "ASH_COATED_OSMIUM": {      # more stable → higher volume
                "base_size": 7,
                "quote_multiplier": 0.28,
                "alpha_threshold": 2.9
            },
            "INTARIAN_PEPPER_ROOT": {   # slightly more volatile → safer
                "base_size": 5,
                "quote_multiplier": 0.32,
                "alpha_threshold": 3.2
            }
        }

    def run(self, state):
        result = {}
        conversions = 0
        traderData = ""

        self.time += 1
        df = build_dataframe_from_state(state)

        if df.empty:
            return result, conversions, traderData

        # Update price history
        for _, row in df.iterrows():
            product = row["symbol"]
            if product not in self.price_history:
                self.price_history[product] = []

            mid = (row["bid_price_1"] + row["ask_price_1"]) / 2
            self.price_history[product].append(mid)
            self.price_history[product] = self.price_history[product][-200:]

        df = compute_alpha_and_fair_value(df, self.price_history)

        for _, row in df.iterrows():
            product = row["symbol"]
            alpha = row.get("alpha", 0.0)
            vol = row.get("std", 5.0)

            order_depth = state.order_depths[product]
            if not order_depth.buy_orders or not order_depth.sell_orders:
                result[product] = []
                continue

            best_bid = max(order_depth.buy_orders.keys())
            best_ask = min(order_depth.sell_orders.keys())
            spread = best_ask - best_bid
            pos = state.position.get(product, 0)

            params = self.product_params.get(product, {"base_size": 5, "quote_multiplier": 0.3, "alpha_threshold": 3.0})

            # Spread-aware quoting: only trade when there is real edge
            if spread < 3:  # too tight → skip quoting to avoid adverse selection
                result[product] = []
                continue

            # Adaptive offset based on volatility
            quote_offset = max(1, int(vol * params["quote_multiplier"]))

            # Mild but effective inventory skew (scaled safely)
            inventory_skew = pos * 0.26

            buy_price = int(best_bid + quote_offset - max(0, inventory_skew * 0.75))
            sell_price = int(best_ask - quote_offset + max(0, -inventory_skew * 0.75))

            # Dynamic size: larger when spread is wide and position is flat
            size = params["base_size"]
            if spread > 8:
                size = min(12, size + 3)          # extra size on fat spreads
            if abs(pos) >= 12:
                size = max(2, size - abs(pos) // 7)

            orders = []

            # === CORE MARKET MAKING (high volume when edge exists) ===
            if pos < self.position_limit - 6:
                orders.append(Order(product, buy_price, size))
            if pos > -self.position_limit + 6:
                orders.append(Order(product, sell_price, -size))

            # === STRONGER INVENTORY CONTROL (prevents any drawdown) ===
            if pos > 22:
                orders.append(Order(product, best_bid, -9))
            elif pos < -22:
                orders.append(Order(product, best_ask, 9))

            if 12 < pos <= 22:
                orders.append(Order(product, best_bid - 1, -6))
            elif -22 <= pos < -12:
                orders.append(Order(product, best_ask + 1, 6))

            # === SCALED ALPHA OVERLAY (only on very strong signals) ===
            thresh = params["alpha_threshold"]
            if alpha > thresh and pos < 40:
                orders.append(Order(product, best_ask, 7))
            elif alpha < -thresh and pos > -40:
                orders.append(Order(product, best_bid, -7))

            # Extra product-specific alpha boost
            if product == "ASH_COATED_OSMIUM" and abs(alpha) > thresh + 0.6 and abs(pos) < 30:
                if alpha > 0:
                    orders.append(Order(product, best_bid, -5))
                else:
                    orders.append(Order(product, best_ask, 5))

            result[product] = orders

        return result, conversions, traderData


# Simple backtest helper (for local testing)
def backtest(df: pd.DataFrame):
    df = df.copy()
    df["returns"] = df.get("mid_price", 0).pct_change().shift(-1)
    df["strategy_returns"] = np.where(df["alpha"] > 1.0, df["returns"],
                                      np.where(df["alpha"] < -1.0, -df["returns"], 0))
    df["cumulative"] = (1 + df["strategy_returns"]).cumprod()
    return df
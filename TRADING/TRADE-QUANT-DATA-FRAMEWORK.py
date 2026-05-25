# ================================
# Trade-Profit-Quant-Framework.py
# ENHANCED HIGH-PROFIT VERSION v2 (very close to original safe base)
# Goal: Scale from hundreds → 10k–50k+ PnL
# Upgrades:
# - Higher position limit + larger base/dynamic sizes
# - Milder inventory skew (0.24) with light alpha adjustment
# - Stronger controlled liquidation
# - Slightly lower alpha thresholds + bigger alpha bets
# - Tighter quote offset + adjusted spread gate for more activity
# - Per-product tuning scaled up
# ================================
import pandas as pd
import numpy as np
from datamodel import Order

# ================================
# FAIR VALUE + ALPHA CALCULATION (unchanged)
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
# BUILD DATAFRAME (unchanged)
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
# TRADER CLASS - SCALED FOR 10K+
# ================================
class Trader:
    def __init__(self):
        self.price_history = {}
        self.time = 0
        self.position_limit = 200  # increased for volume scaling

        # Per-product parameters - scaled up from your original
        self.product_params = {
            "ASH_COATED_OSMIUM": {   # more stable → push harder
                "base_size": 12,
                "quote_multiplier": 0.25,
                "alpha_threshold": 2.6
            },
            "INTARIAN_PEPPER_ROOT": { # slightly more volatile → still aggressive but safer
                "base_size": 9,
                "quote_multiplier": 0.29,
                "alpha_threshold": 2.9
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

            params = self.product_params.get(product, {"base_size": 8, "quote_multiplier": 0.27, "alpha_threshold": 2.8})

            # Spread-aware quoting: only trade when there is real edge (slightly relaxed)
            if spread < 4:   # was 3 → allows a bit more activity
                result[product] = []
                continue

            # Adaptive offset (slightly tighter than original for better fills)
            quote_offset = max(1, int(vol * params["quote_multiplier"]))

            # Milder but effective inventory skew (0.24)
            inventory_skew = pos * 0.24
            # Light alpha-aware adjustment: reduce opposing skew on strong signals
            if abs(alpha) > 2.0:
                inventory_skew *= 0.85

            buy_price = int(best_bid + quote_offset - max(0, inventory_skew * 0.75))
            sell_price = int(best_ask - quote_offset + max(0, -inventory_skew * 0.75))

            # Dynamic size: larger when spread is wide / alpha strong / position flat
            size = params["base_size"]
            if spread > 8:
                size = min(22, size + 7)
            if abs(alpha) > 3.5:
                size = min(25, size + 5)
            if abs(pos) >= 15:
                size = max(3, size - abs(pos) // 8)

            orders = []

            # === CORE MARKET MAKING (high volume when edge exists) ===
            if pos < self.position_limit - 8:
                orders.append(Order(product, buy_price, size))
            if pos > -self.position_limit + 8:
                orders.append(Order(product, sell_price, -size))

            # === STRONGER INVENTORY CONTROL (scaled for higher limits) ===
            if pos > 35:
                orders.append(Order(product, best_bid, -14))
            elif pos < -35:
                orders.append(Order(product, best_ask, 14))
            if 18 < pos <= 35:
                orders.append(Order(product, best_bid - 1, -9))
            elif -35 <= pos < -18:
                orders.append(Order(product, best_ask + 1, 9))

            # === SCALED ALPHA OVERLAY (stronger on very clear signals) ===
            thresh = params["alpha_threshold"]
            alpha_size = 11 if abs(alpha) > thresh + 0.7 else 8
            if alpha > thresh and pos < 70:
                orders.append(Order(product, best_ask, alpha_size))   # your original direction
            elif alpha < -thresh and pos > -70:
                orders.append(Order(product, best_bid, -alpha_size))

            # Extra Osmium boost (scaled)
            if product == "ASH_COATED_OSMIUM" and abs(alpha) > thresh + 0.8 and abs(pos) < 50:
                if alpha > 0:
                    orders.append(Order(product, best_bid, -8))
                else:
                    orders.append(Order(product, best_ask, 8))

            result[product] = orders

        return result, conversions, traderData

# Simple backtest helper (unchanged)
def backtest(df: pd.DataFrame):
    df = df.copy()
    df["returns"] = df.get("mid_price", 0).pct_change().shift(-1)
    df["strategy_returns"] = np.where(df["alpha"] > 1.0, df["returns"], np.where(df["alpha"] < -1.0, -df["returns"], 0))
    df["cumulative"] = (1 + df["strategy_returns"]).cumprod()
    return df
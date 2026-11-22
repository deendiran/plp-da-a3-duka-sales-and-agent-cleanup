# Data generator to create duka_sales.csv
import numpy as np
import pandas as pd

rng = np.random.default_rng(2026)
n = 1000

products = {
    "Phone": 15000,
    "Laptop": 65000,
    "Headphones": 2500,
    "Tablet": 28000,
    "Charger": 1200,
}

sales = pd.DataFrame({
    "order_id": range(1001, 1001 + n),
    "order_date": pd.to_datetime("2026-01-01")
    + pd.to_timedelta(rng.integers(0, 180, n), unit="D"),
    "branch": rng.choice(
        ["Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret"],
        n,
        p=[0.4, 0.2, 0.15, 0.15, 0.1],
    ),
    "product": rng.choice(list(products), n),
    "quantity": rng.integers(1, 6, n),
    "channel": rng.choice(
        ["In-store", "Online", "Phone order"], n, p=[0.55, 0.35, 0.10]
    ),
})

sales["unit_price"] = sales["product"].map(products)
sales.to_csv("duka_sales.csv", index=False)

# Data generator to create agent_transactions.csv and agents.csv
rng_a = np.random.default_rng(44)
p = 600

agents = pd.DataFrame({
    "agent_id": [f"AG{i:03d}" for i in range(1, 21)],
    "county": rng_a.choice(
        ["Nairobi", "Kiambu", "Nakuru", "Mombasa", "Kisumu"], 20
    ),
    "onboarded": pd.date_range("2024-01-01", periods=20, freq="MS").strftime(
        "%Y-%m-%d"
    ),
})

txns = pd.DataFrame({
    "txn_id": [f"TX{i:05d}" for i in range(1, p + 1)],
    "agent_id": rng_a.choice(agents["agent_id"], p),
    "txn_type": rng_a.choice(
        ["Deposit", "withdrawal", "DEPOSIT ", "Withdrawal", "deposit"], p
    ),
    "amount": rng_a.lognormal(7.5, 0.8, p).round(0).astype(str),
    "txn_date": (
        pd.to_datetime("2026-03-01")
        + pd.to_timedelta(rng_a.integers(0, 60, p), unit="D")
    ).strftime("%Y-%m-%d"),
})

# Note: sample from p (600) rather than n (1000) to prevent index out of bounds
idx = rng_a.choice(p, 30, replace=False)
txns.loc[idx[:15], "amount"] = np.nan
txns.loc[idx[15:20], "amount"] = "N/A"
txns.loc[idx[20:25], "amount"] = "250000"
txns.loc[idx[25:], "txn_date"] = txns.loc[idx[25:], "txn_date"].str.replace(
    "-", "/"
)

txns = pd.concat([txns, txns.sample(12, random_state=1)], ignore_index=True)
txns.loc[rng_a.choice(len(txns), 8, replace=False), "agent_id"] = "AG099"

agents.to_csv("agents.csv", index=False)
txns.to_csv("agent_transactions.csv", index=False)